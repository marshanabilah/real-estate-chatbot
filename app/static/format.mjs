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

export function formatBlocks(text) {
  const blocks = [];
  let items = [];
  const flushList = () => {
    if (items.length) blocks.push({ type: 'list', items });
    items = [];
  };
  for (const line of text.split('\n')) {
    const bullet = /^[-*]\s+(.+)$/.exec(line.trim());
    if (bullet) {
      items.push(bullet[1]);
    } else if (line.trim()) {
      flushList();
      blocks.push({ type: 'paragraph', value: line.trim() });
    } else {
      flushList();
    }
  }
  flushList();
  return blocks;
}

function appendInlineText(container, text) {
  formatSegments(text).forEach(segment => {
    if (segment.type === 'strong') {
      const strong = document.createElement('strong');
      strong.textContent = segment.value;
      container.append(strong);
    } else {
      container.append(document.createTextNode(segment.value));
    }
  });
}

export function appendFormattedText(container, text) {
  formatBlocks(text).forEach(block => {
    if (block.type === 'list') {
      const list = document.createElement('ul');
      block.items.forEach(item => {
        const listItem = document.createElement('li');
        appendInlineText(listItem, item);
        list.append(listItem);
      });
      container.append(list);
    } else {
      const paragraph = document.createElement('p');
      appendInlineText(paragraph, block.value);
      container.append(paragraph);
    }
  });
}
