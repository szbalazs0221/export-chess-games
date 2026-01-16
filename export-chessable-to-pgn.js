const COURSE_NAME = document.querySelector('.courseUI-bookName').title;

async function main() {
  console.log(`Getting lines for course: ${COURSE_NAME}`);
  while (true) {
    await sleep(3000);
    const variations = parseVariations();
    savePgn(variations);
    if (hasNextChapter()) {
      navigateToNextChapter();
    } else {
      console.log('This it the last chapter, export completed!');
      break;
    }
  }
}

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));

function downloadToFile(filename, text) {
  console.log(`Downloading variations into ${filename}`);
  var pom = document.createElement('a');
  pom.setAttribute(
    'href',
    'data:text/plain;charset=utf-8,' + encodeURIComponent(text)
  );
  pom.setAttribute('download', filename);

  if (document.createEvent) {
    var event = document.createEvent('MouseEvents');
    event.initEvent('click', true, true);
    pom.dispatchEvent(event);
  } else {
    pom.click();
  }
}

function hasNextChapter() {
  return document.querySelector('.ui23-button-iconAfter') || false;
}

function getChapterTitle() {
  return document.querySelectorAll('h1')[0].textContent.slice(8); // removing the "Chapters" part
}

function parseVariations() {
  const VARIATION_CARDS_SELECTOR = document.querySelectorAll('.variation-card');
  // Capturing chapter title - This is going to be the White player's name
  const chapterTitle = getChapterTitle();
  // Capturing variations
  const variations = [];
  VARIATION_CARDS_SELECTOR.forEach((variation) => {
    const variationName = variation.querySelectorAll('div')[0].textContent;
    const moves = variation.querySelector('.variation-card__moves').textContent;
    const priority = variation.querySelector('.ui23-label-important')
      ? true
      : false;
    const alternative = variation.querySelector('.ui23-label-alternative')
      ? true
      : false;
    const informational = variation.querySelector('.ui23-label-informational')
      ? true
      : false;
    variations.push({
      white: chapterTitle,
      black: variationName,
      moves,
      priority,
      alternative,
      informational,
    });
  });
  console.log(
    `Processed ${variations.length} variations for chapter: ${chapterTitle}`
  );
  return variations;
}

function navigateToNextChapter() {
  const currentChapterTitle = getChapterTitle();
  console.log('Navigating to next chapter...');
  $('.ui23-button-iconAfter').click();
}

function savePgn(variations) {
  const chapterTitle = getChapterTitle();
  console.log(`Creating pgn file for chapter: ${chapterTitle}`);
  // Putting together the PGN file
  const pgnContent = [];
  variations.forEach((variation) => {
    const headerInfo = `[White "${variation.white}"]\n[Black "${variation.black}"]\n`;
    const additionalTags = `[Priority "${variation.priority}"]\n[Alternative "${variation.alternative}"]\n[Informational "${variation.informational}"]\n\n`;
    pgnContent.push(`${headerInfo}${additionalTags}${variation.moves}\n`);
  });
  const sanitizedCourseName = COURSE_NAME.toLowerCase()
    .replaceAll(' ', '-')
    .replaceAll('.', '');
  const sanitizedChapterName = chapterTitle
    .toLowerCase()
    .replaceAll(' ', '-')
    .replaceAll('.', '');
  const fileName = `${sanitizedCourseName}-${sanitizedChapterName}.pgn`;
  downloadToFile(fileName, pgnContent.join('\n'));
}

await main();
