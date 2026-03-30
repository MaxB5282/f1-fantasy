require('dotenv').config();
const express = require('express');
const path = require('path');
const crypto = require('crypto');
const { createClient } = require('@supabase/supabase-js');

const app = express();
const PORT = process.env.PORT || 3000;

// ── Supabase ───────────────────────────────────────────────────────────────────
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

// ── Auth ───────────────────────────────────────────────────────────────────────
const APP_PASSWORD = process.env.APP_PASSWORD || 'changeme';
const COOKIE_NAME = 'jt_auth';
const COOKIE_MAX_AGE = 30 * 24 * 60 * 60; // 30 days in seconds

function makeToken() {
  return crypto.createHash('sha256').update(APP_PASSWORD + 'job-tracker-v1').digest('hex');
}

function parseCookies(req) {
  const cookies = {};
  (req.headers.cookie || '').split(';').forEach((c) => {
    const [k, ...v] = c.trim().split('=');
    if (k) cookies[k.trim()] = decodeURIComponent(v.join('='));
  });
  return cookies;
}

function requireAuth(req, res, next) {
  if (req.path === '/login' || req.path === '/api/login') return next();
  const cookies = parseCookies(req);
  if (cookies[COOKIE_NAME] === makeToken()) return next();
  if (req.path.startsWith('/api/')) return res.status(401).json({ error: 'Unauthorized' });
  res.redirect('/login');
}

// ── Middleware ─────────────────────────────────────────────────────────────────
app.use(express.json());
app.use(requireAuth);
app.use(express.static(path.join(__dirname, 'public')));

// ── Auth routes ────────────────────────────────────────────────────────────────
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.post('/api/login', (req, res) => {
  if (req.body.password !== APP_PASSWORD) {
    return res.status(401).json({ error: 'Wrong password.' });
  }
  res.setHeader(
    'Set-Cookie',
    `${COOKIE_NAME}=${makeToken()}; Max-Age=${COOKIE_MAX_AGE}; Path=/; HttpOnly; SameSite=Strict`
  );
  res.json({ ok: true });
});

app.post('/api/logout', (req, res) => {
  res.setHeader('Set-Cookie', `${COOKIE_NAME}=; Max-Age=0; Path=/; HttpOnly; SameSite=Strict`);
  res.json({ ok: true });
});

// ── Job routes ─────────────────────────────────────────────────────────────────
const STATUS_ORDER = { 'not applied': 0, applied: 1, 'heard back': 2, offer: 3, rejected: 4 };

app.get('/api/jobs', async (req, res) => {
  const { data, error } = await supabase
    .from('jobs')
    .select('*')
    .order('date_added', { ascending: false });

  if (error) return res.status(500).json({ error: error.message });

  const sorted = data.sort((a, b) => {
    const diff = (STATUS_ORDER[a.status] ?? 9) - (STATUS_ORDER[b.status] ?? 9);
    if (diff !== 0) return diff;
    return (b.date_added || '').localeCompare(a.date_added || '');
  });

  res.json(sorted);
});

app.post('/api/jobs', async (req, res) => {
  const { title, url, salary, notes } = req.body;
  if (!title) return res.status(400).json({ error: 'Title is required.' });

  const { data, error } = await supabase
    .from('jobs')
    .insert({
      title: title.trim(),
      url: url?.trim() || null,
      salary: salary?.trim() || null,
      notes: notes?.trim() || null,
      status: 'not applied',
      date_added: new Date().toISOString().split('T')[0],
    })
    .select()
    .single();

  if (error) return res.status(500).json({ error: error.message });
  res.json(data);
});

app.patch('/api/jobs/:id', async (req, res) => {
  const allowed = ['status', 'notes', 'salary', 'title', 'url'];
  const updates = {};
  for (const field of allowed) {
    if (req.body[field] !== undefined) updates[field] = req.body[field];
  }

  const { error } = await supabase
    .from('jobs')
    .update(updates)
    .eq('id', req.params.id);

  if (error) return res.status(500).json({ error: error.message });
  res.json({ ok: true });
});

app.delete('/api/jobs/:id', async (req, res) => {
  const { error } = await supabase
    .from('jobs')
    .delete()
    .eq('id', req.params.id);

  if (error) return res.status(500).json({ error: error.message });
  res.json({ ok: true });
});

// ── Start ──────────────────────────────────────────────────────────────────────
app.listen(PORT, () => console.log(`Job tracker → http://localhost:${PORT}`));
