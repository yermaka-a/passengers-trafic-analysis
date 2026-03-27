const puppeteer = require('puppeteer');

(async () => {
  console.log('[TEST] Запуск браузера...');
  const browser = await puppeteer.launch({ 
    headless: false,
    slowMo: 100
  });
  
  const page = await browser.newPage();
  
  // Включаем логирование из браузера
  page.on('console', msg => {
    console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`);
  });
  
  console.log('[TEST] Переход на страницу...');
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(3000);
  
  console.log('[TEST] Клик по карте для создания полигона...');
  await page.click('#map', { position: { x: 400, y: 300 } });
  await page.waitForTimeout(500);
  await page.click('#map', { position: { x: 500, y: 300 } });
  await page.waitForTimeout(500);
  await page.click('#map', { position: { x: 450, y: 400 } });
  await page.waitForTimeout(500);
  
  console.log('[TEST] Нажатие кнопки Добавить...');
  await page.click('button:has-text("Добавить")');
  await page.waitForTimeout(1000);
  
  console.log('[TEST] Поиск color input...');
  const colorInput = await page.$('input[type="color"]');
  if (!colorInput) {
    console.error('[TEST] Color input не найден!');
    await browser.close();
    return;
  }
  
  const currentValue = await page.evaluate(el => el.value, colorInput);
  console.log('[TEST] Текущий цвет:', currentValue);
  
  console.log('[TEST] Изменение цвета на красный...');
  await colorInput.evaluate(el => {
    el.value = '#ff0000';
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  });
  
  await page.waitForTimeout(1000);
  
  const newValue = await page.evaluate(el => el.value, colorInput);
  console.log('[TEST] Новый цвет:', newValue);
  
  console.log('[TEST] Скриншот...');
  await page.screenshot({ path: 'test-puppeteer-color.png' });
  
  await page.waitForTimeout(5000);
  await browser.close();
  console.log('[TEST] Завершено!');
})();
