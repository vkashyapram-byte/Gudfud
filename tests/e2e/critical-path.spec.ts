import { test, expect } from '@playwright/test';

test.describe('Gud Fud MVP Critical Path', () => {
  test('User can execute a search and view structural results', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Execute search for a known test product
    // Note: Assumes a search input exists on the homepage (we will target the /search route directly if no input exists yet)
    await page.goto('/search?q=test-product');

    // Verify search results page renders the structural CSS grid
    const searchGrid = page.locator('.grid');
    await expect(searchGrid).toBeVisible();

    // Verify sharp-edged structural borders are present (not rounded)
    const firstResult = searchGrid.locator('a').first();
    // In Tailwind, our rounded utilities were overridden to 4px max, but we can verify classes
    await expect(firstResult).toHaveClass(/border-brand-border|border-brand-neutral/);
  });

  test('Admin dashboard correctly renders data blocks', async ({ page }) => {
    // Navigate directly to admin dashboard
    await page.goto('/admin');

    // Assert 'Pending Reviews' block renders correctly
    const pendingReviewsBlock = page.locator('text=Pending Reviews');
    await expect(pendingReviewsBlock).toBeVisible();

    // Verify the admin layout sidebar is present
    const sidebar = page.locator('aside');
    await expect(sidebar).toBeVisible();
    await expect(sidebar).toContainText('Review Queue');
  });
});
