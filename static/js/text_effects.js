document.querySelectorAll('.word-container').forEach(function(button) {
	const wordContainerEl = button;
	const word = wordContainerEl.getAttribute("data-word");
	const wordRepeatTimes = wordContainerEl.getAttribute("data-word-repeat");
	const textColorsArray = wordContainerEl.getAttribute("data-text-colors").split(",");

	for (let i = 0; i < wordRepeatTimes; i++) {
		const wordEl = document.createElement("span");
		wordEl.className = "word";
		wordEl.style.setProperty("--word-index", i);
		wordEl.style.setProperty("--color", textColorsArray[i]);
		for (let j = 0; j < word.length; j++) {
			const charEl = document.createElement("span");
			charEl.className = "char";
			charEl.style.setProperty("--char-index", j);
			charEl.innerHTML = word[j];
			wordEl.appendChild(charEl);
			if (word[j] == ' '){
				charEl.style.marginLeft = '1rem'
			}
		}
		wordContainerEl.appendChild(wordEl);
	}
});

const wordContainerEl = document.querySelector("[data-word]");
const word = wordContainerEl.getAttribute("data-word");
const wordRepeatTimes = wordContainerEl.getAttribute("data-word-repeat");
const textColorsArray = wordContainerEl.getAttribute("data-text-colors").split(",");

for (let i = 0; i < wordRepeatTimes; i++) {
	const wordEl = document.createElement("span");
	wordEl.className = "word";
	wordEl.style.setProperty("--word-index", i);
	wordEl.style.setProperty("--color", textColorsArray[i]);
	for (let j = 0; j < word.length; j++) {
		const charEl = document.createElement("span");
		charEl.className = "char";
		charEl.style.setProperty("--char-index", j);
		charEl.innerHTML = word[j];
		wordEl.appendChild(charEl);
		if (word[j] == ' '){
			charEl.style.marginLeft = '1rem'
		}
	}
	wordContainerEl.appendChild(wordEl);
}
