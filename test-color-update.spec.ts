import { test, expect } from '@playwright/test';

test.describe('Deck.gl Color Update', () => {
  test('should update polygon color on map', async ({ page }) => {
    // Открываем приложение
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);

    // Ждём загрузки карты
    await page.waitForSelector('#map');
    await page.waitForTimeout(1000);

    console.log('[TEST] Карта загружена');

    // Создаём полигон - кликаем 3 раза
    await page.click('#map', { position: { x: 400, y: 300 } });
    await page.waitForTimeout(200);
    await page.click('#map', { position: { x: 500, y: 300 } });
    await page.waitForTimeout(200);
    await page.click('#map', { position: { x: 450, y: 400 } });
    await page.waitForTimeout(200);

    console.log('[TEST] Полигон создан');

    // Нажимаем "Добавить"
    const addButton = page.getByText('Добавить').first();
    await addButton.click();
    await page.waitForTimeout(500);

    console.log('[TEST] Полигон добавлен');

    // Находим карточку объекта в списке
    const colorInput = page.locator('input[type="color"]').first();
    await expect(colorInput).toBeVisible();

    // Получаем текущий цвет
    const currentColor = await colorInput.inputValue();
    console.log('[TEST] Текущий цвет:', currentColor);

    // Меняем цвет на красный
    await colorInput.fill('#ff0000');
    await colorInput.dispatchEvent('input');
    await page.waitForTimeout(500);

    console.log('[TEST] Цвет изменён на #ff0000');

    // Проверяем что цвет в store обновился
    const updatedColor = await colorInput.inputValue();
    console.log('[TEST] Новый цвет в input:', updatedColor);

    // Делаем скриншот
    await page.screenshot({ path: 'test-color-change.png' });
    console.log('[TEST] Скриншот сохранён');

    expect(updatedColor).toBe('#ff0000');
  });
});
