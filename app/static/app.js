const results = document.querySelector('#results');
const resultCount = document.querySelector('#result-count');
const filters = document.querySelector('#filters');
const answer = document.querySelector('#answer');

const money = (value, currency) => value ? new Intl.NumberFormat('en-SA', { style: 'currency', currency, maximumFractionDigits: 0 }).format(value) : 'Price on request';
const node = (tag, text, className) => {
  const element = document.createElement(tag);
  if (text) element.textContent = text;
  if (className) element.className = className;
  return element;
};

function sourceLink(record) {
  const link = node('a', 'View public source ↗');
  link.href = record.source_url;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  return link;
}

function card(record) {
  const article = node('article', null, 'card');
  const top = node('div', null, 'card-top');
  top.append(node('span', record.source, 'source'), node('span', record.record_type));
  const place = [record.district, record.city, record.country].filter(Boolean).join(', ');
  const facts = [record.property_type, record.bedrooms && `${record.bedrooms} bedrooms`, record.area_sqm && `${record.area_sqm} sqm`].filter(Boolean).join(' · ');
  article.append(top, node('h3', record.title), node('p', place, 'place'), node('p', facts || 'Project details', 'facts'), node('p', money(record.price, record.currency || 'SAR'), 'price'), sourceLink(record));
  return article;
}

function showStatus(message, isError = false) {
  results.replaceChildren(node('p', message, `status${isError ? ' error' : ''}`));
}

async function loadProperties() {
  const params = new URLSearchParams();
  for (const [key, value] of new FormData(filters).entries()) {
    const cleaned = value.replaceAll(',', '').trim();
    if (cleaned) params.set(key, cleaned);
  }
  results.setAttribute('aria-busy', 'true');
  showStatus('Loading records…');
  try {
    const response = await fetch(`/api/properties?${params}`);
    if (!response.ok) throw new Error('Property request failed');
    const payload = await response.json();
    resultCount.textContent = `${payload.total} records`;
    results.replaceChildren(...(payload.items.length ? payload.items.map(card) : [node('p', 'No matching records. Try a wider search.', 'status')]));
  } catch {
    showStatus('The catalog could not be loaded. Please try again.', true);
  } finally {
    results.setAttribute('aria-busy', 'false');
  }
}

filters.addEventListener('submit', event => { event.preventDefault(); loadProperties(); });
document.querySelector('#chat-form').addEventListener('submit', async event => {
  event.preventDefault();
  const question = document.querySelector('#question').value.trim();
  if (!question) return;
  answer.hidden = false;
  answer.textContent = 'Searching the catalog…';
  try {
    const response = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question }) });
    if (!response.ok) throw new Error('Chat request failed');
    const payload = await response.json();
    const sources = node('p', null, 'citations');
    sources.append(node('strong', 'Sources: '));
    if (payload.sources.length) {
      payload.sources.forEach((source, index) => {
        if (index) sources.append(document.createTextNode(' · '));
        const link = node('a', source.title);
        link.href = source.source_url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        sources.append(link);
      });
    } else {
      sources.append(document.createTextNode('No matching record'));
    }
    const responseText = node('div', null, 'answer-text');
    appendFormattedText(responseText, payload.answer);
    answer.replaceChildren(responseText, sources, node('p', payload.disclaimer, 'fineprint'));
  } catch {
    answer.textContent = 'The assistant could not answer right now. Please try again.';
  }
});

loadProperties();
import { appendFormattedText } from './format.mjs';

