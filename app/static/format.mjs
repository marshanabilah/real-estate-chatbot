export function formatSegments(text) {
  const segments = [];
  const pattern = /\*\*([^*\n]+)\*\*/g;
  let cursor = 0;
  for (const match of text.matchAll(pattern)) {
    if (match.index > cursor) segments.push({ type: 'text', value: text.slice(cursor, match.index) });
    segments.push({ type: 'strong', value: match[1] });
    cursor = match.index + match[0].length;
  }
  if (cursor < text.length || !segments.length) segments.push({ type: 'text', value: text.slice(cursor) });
  return segments;
}

function appendTextWithBreaks(container, text) {
  text.split('\n').forEach((line, index) => {
    if (index) container.append(document.createElement('br'));
    container.append(document.createTextNode(line));
  });
}

export function appendFormattedText(container, text) {
  formatSegments(text).forEach(segment => {
    if (segment.type === 'strong') {
      const strong = document.createElement('strong');
      strong.textContent = segment.value;
      container.append(strong);
    } else {
      appendTextWithBreaks(container, segment.value);
    }
  });
}
