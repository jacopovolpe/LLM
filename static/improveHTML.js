function improveHTML(text) {
  console.log(text);
  
  improved = text
    .replace(/```html|```|'''html|'''/g, '') 
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\$(.*?)\$/g, '<span class="latex">$1</span>');

  improved = convertToHTML(improved);
  
  console.log(improved);
  return improved;
}

function convertToHTML(markdown) {
  const lines = markdown.split('\n');
  let html = '';
  let paragraphBuffer = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Gestione della linea vuota
    if (line === '') {
      if (paragraphBuffer.length > 0) {
        html += `<p>${paragraphBuffer.join(' ')}</p>\n`;
        paragraphBuffer = [];
      }
      continue;
    }

    // Intestazioni
    const headerMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headerMatch) {
      if (paragraphBuffer.length > 0) {
        html += `<p>${paragraphBuffer.join(' ')}</p>\n`;
        paragraphBuffer = [];
      }
      const level = headerMatch[1].length;
      html += `<h${level}>${headerMatch[2]}</h${level}>\n`;
      continue;
    }

    // Blockquote
    const blockquoteMatch = line.match(/^>\s+(.*)$/);
    if (blockquoteMatch) {
      if (paragraphBuffer.length > 0) {
        html += `<p>${paragraphBuffer.join(' ')}</p>\n`;
        paragraphBuffer = [];
      }
      html += `<blockquote>${blockquoteMatch[1]}</blockquote>\n`;
      continue;
    }

    // Caso predefinito: accumula la linea nel buffer del paragrafo
    paragraphBuffer.push(line);
  }

  // Processa eventuale contenuto residuo nel buffer
  if (paragraphBuffer.length > 0) {
    html += `<p>${paragraphBuffer.join(' ')}</p>\n`;
  }

  return html;
}

