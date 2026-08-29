document.querySelectorAll('[data-year]').forEach((el) => {
  el.textContent = new Date().getFullYear();
});

const languageButtons = document.querySelectorAll('[data-set-language]');
const languagePage = document.querySelector('.language-page');

function setResearchPageLanguage(language) {
  if (!languagePage) return;
  const selected = language === 'en' ? 'en' : 'ar';
  languagePage.dataset.language = selected;
  languagePage.lang = selected;
  languagePage.dir = selected === 'ar' ? 'rtl' : 'ltr';
  document.querySelectorAll('[data-i18n-en][data-i18n-ar]').forEach((element) => {
    element.textContent = element.dataset[selected === 'ar' ? 'i18nAr' : 'i18nEn'];
  });
  languageButtons.forEach((button) => {
    button.setAttribute('aria-pressed', button.dataset.setLanguage === selected ? 'true' : 'false');
  });
  try {
    localStorage.setItem('researchEffortLanguage', selected);
  } catch (error) {
    // Local storage can be unavailable in strict browser modes.
  }
}

if (languagePage) {
  let storedLanguage = 'ar';
  try {
    storedLanguage = localStorage.getItem('researchEffortLanguage') || 'ar';
  } catch (error) {
    storedLanguage = 'ar';
  }
  setResearchPageLanguage(storedLanguage);
  languageButtons.forEach((button) => {
    button.addEventListener('click', () => setResearchPageLanguage(button.dataset.setLanguage));
  });
}
