const TITLE_SELECTOR = document.querySelectorAll('h1')[0];
const VARIATION_CARDS_SELECTOR = document.querySelectorAll('.variation-card');

// Capturing chapter title - This is going to be the White player's name
const chapterTitle = TITLE_SELECTOR.textContent.slice(8); // removing the "Chapters" part

// Capturing variations
const variations = [];
VARIATION_CARDS_SELECTOR.forEach((variation) => {
  const variationName = variation.querySelectorAll('div')[0].textContent;
  const moves = variation.querySelector('.variation-card__moves').textContent;
  variations.push({
    white: chapterTitle,
    black: variationName,
    moves,
  });
});

// Putting together the PGN file
const pgnContent = [];
variations.forEach((variation) => {
  // Creating the header first
  const variationData = `[White "${variation.white}"]\n[Black "${variation.black}"]\n\n${variation.moves}\n`;
  pgnContent.push(variationData);
});
console.log(pgnContent.join('\n'));
