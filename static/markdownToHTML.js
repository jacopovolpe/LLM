function convertMarkdownToHTML(markdown) {
    // Divide il testo in righe
    const lines = markdown.split('\n');
    let html = '';
    let inOrderedList = false;
    let inUnorderedList = false;
    let inCodeBlock = false;
    let codeBlockContent = '';
    let paragraphBuffer = [];
  
    // Funzione per processare la formattazione inline (grassetto, corsivo, inline code, link)
    function processInlineFormatting(text) {
      // Grassetto: **testo**
      text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Corsivo: *testo*
      text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
      // Codice inline: `codice`
      text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
      // Link: [testo](url)
      text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
      return text;
    }
  
    // Funzione per creare un paragrafo dai contenuti accumulati
    function flushParagraph() {
      if (paragraphBuffer.length > 0) {
        const paragraph = processInlineFormatting(paragraphBuffer.join(' '));
        html += `<p>${paragraph}</p>\n`;
        paragraphBuffer = [];
      }
    }
  
    // Scorriamo tutte le righe
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
  
      // Gestione dei blocchi di codice
      if (line.trim().startsWith('```')) {
        if (!inCodeBlock) {
          // Avvio blocco di codice: chiudiamo eventuali paragrafi o liste aperte
          flushParagraph();
          if (inOrderedList) {
            html += '</ol>\n';
            inOrderedList = false;
          }
          if (inUnorderedList) {
            html += '</ul>\n';
            inUnorderedList = false;
          }
          inCodeBlock = true;
          codeBlockContent = '';
        } else {
          // Fine blocco di codice
          inCodeBlock = false;
          html += `<pre><code>${codeBlockContent}</code></pre>\n`;
        }
        continue;
      }
      if (inCodeBlock) {
        codeBlockContent += line + '\n';
        continue;
      }
  
      // Se la linea è vuota, chiudiamo paragrafi o liste aperte
      if (line.trim() === '') {
        flushParagraph();
        if (inOrderedList) {
          html += '</ol>\n';
          inOrderedList = false;
        }
        if (inUnorderedList) {
          html += '</ul>\n';
          inUnorderedList = false;
        }
        continue;
      }
  
      // Controllo per header (linee che iniziano con #)
      let headerMatch = line.match(/^(#{1,6})\s+(.*)$/);
      if (headerMatch) {
        flushParagraph();
        if (inOrderedList) {
          html += '</ol>\n';
          inOrderedList = false;
        }
        if (inUnorderedList) {
          html += '</ul>\n';
          inUnorderedList = false;
        }
        let level = headerMatch[1].length;
        let headerText = processInlineFormatting(headerMatch[2]);
        html += `<h${level}>${headerText}</h${level}>\n`;
        continue;
      }
  
      // Controllo per elementi di lista ordinata (es. "1. testo")
      let orderedMatch = line.match(/^\s*(\d+)\.\s+(.*)$/);
      if (orderedMatch) {
        flushParagraph();
        if (!inOrderedList) {
          if (inUnorderedList) {
            html += '</ul>\n';
            inUnorderedList = false;
          }
          html += '<ol>\n';
          inOrderedList = true;
        }
        let listItem = processInlineFormatting(orderedMatch[2]);
        html += `<li>${listItem}</li>\n`;
        continue;
      }
  
      // Controllo per elementi di lista non ordinata (es. "- testo" o "* testo")
      let unorderedMatch = line.match(/^\s*[-\*]\s+(.*)$/);
      if (unorderedMatch) {
        flushParagraph();
        if (!inUnorderedList) {
          if (inOrderedList) {
            html += '</ol>\n';
            inOrderedList = false;
          }
          html += '<ul>\n';
          inUnorderedList = true;
        }
        let listItem = processInlineFormatting(unorderedMatch[1]);
        html += `<li>${listItem}</li>\n`;
        continue;
      }
  
      // Se nessun altro caso viene soddisfatto, accumula la linea per un paragrafo
      paragraphBuffer.push(line.trim());
    }
  
    // Alla fine, flush di eventuali paragrafi o liste ancora aperte
    flushParagraph();
    if (inOrderedList) {
      html += '</ol>\n';
    }
    if (inUnorderedList) {
      html += '</ul>\n';
    }
  
    return html;
  }
  