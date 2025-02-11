import puppeteer from 'puppeteer';
import { mkdir } from 'fs/promises';

const COOKIES = `tailwind_ui_session=${encodeURIComponent('eyJpdiI6Ikt5K0s0VDdZdTJndlYzOGVKLzI5Unc9PSIsInZhbHVlIjoielBOTE9mTWplODd6d1VmMi83c1NDOWlkTE1QZDgvMloxZjZPcFZSMzJ4aU9OT0NnZ0c4R0RzUGZTbjVvWnNzQm13NytZSTR3czdZYnZmM2huYi9Ra0lYVk9XTXJxYzhGbG8yUVhoRGJPZ3AyV2hxVndPSW9hUEhhb0lKK0VoT0wiLCJtYWMiOiI2MTQyNzM4ZGI5YWFjOTczY2JlMGYyMzZlYTkyOWYyMjlmYjE0OWQxZDk4MzEzNTQ5NDU2Y2Q5ODYwMjAxYjJjIiwidGFnIjoiIn0%3D')}; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=${encodeURIComponent('eyJpdiI6IlVxT01KRWo2VEFHQjhnYU5XZURwYmc9PSIsInZhbHVlIjoidUVhNlI0STVHSWI4RFR0L01oS1VDSmN4RnB2MWk0RmludEJzalNVNDZaaXJvM05yblBBRldzcDZxUkJvemh1V2RhT29kZUVrK3I1Mm42ZnVrdWlXaHh6djU1OXB1UkdqaEsrUTFic1lTQ0pMalhQbUJ3S25pbi9Fc3pDc3lYa2hmQlhtbTRTVHZKQ3BOR2p2N2I2eHZtYi9hS3Q2WmoyQmxja2daRm1zS3ZhSmsrYzhyZXdxYTJMNTJZTDk3TUVEeDVKRFpwSUlWcHpjYWFVc0Jwbk9xQm15MTUvYUNyc3dXVzRxOG9xWEpCcz0iLCJtYWMiOiI1YjA0NmIxYTM4OTgyOTI5ODg5MGQ0OTAyZTVhNzA2N2IzMTEwOTVmOGI5ZmY5MGMyMGQyZGQ4MjJiY2I1ZTg5IiwidGFnIjoiIn0%3D')}; XSRF-TOKEN=${encodeURIComponent('eyJpdiI6IlZHbnRLYitoUFNWQjh1d0lPSktid3c9PSIsInZhbHVlIjoiTWFDZFBpbFNYM2dEWnY2amREdUxXamVEQkRkOXlyQnJWSnEvUWZZUHRzcnRQWjEzbk1jOHBTbm5MQzJJUHRNOWk2Mk5VVHZERTdRSC85TVVoYm5zeFRaVGxYem5vcGNISHBzMmNFMFpVd3BoaktwTnBxdFJSZ1JBVkR4RHVxd0giLCJtYWMiOiIwZDAxYjY3ZmNmMmJhOTkzY2E3YzY2ZTI5N2ZjM2NmN2I1Zjc2ZmY0YzljNmJkZDEwYTY3Y2U2ZTA4ZDI1MjcwIiwidGFnIjoiIn0%3D')}`;

async function scrapeUILibrary() {
    const outputDir = "./scraped-components";
    const browser = await puppeteer.launch({
        headless: "new",
        defaultViewport: { width: 1920, height: 1080 }
    });

    try {
        const page = await browser.newPage();
        
        // Set cookies properly with all required fields
        await page.setCookie(
            {
                name: 'tailwind_ui_session',
                value: 'eyJpdiI6Ikt5K0s0VDdZdTJndlYzOGVKLzI5Unc9PSIsInZhbHVlIjoielBOTE9mTWplODd6d1VmMi83c1NDOWlkTE1QZDgvMloxZjZPcFZSMzJ4aU9OT0NnZ0c4R0RzUGZTbjVvWnNzQm13NytZSTR3czdZYnZmM2huYi9Ra0lYVk9XTXJxYzhGbG8yUVhoRGJPZ3AyV2hxVndPSW9hUEhhb0lKK0VoT0wiLCJtYWMiOiI2MTQyNzM4ZGI5YWFjOTczY2JlMGYyMzZlYTkyOWYyMjlmYjE0OWQxZDk4MzEzNTQ5NDU2Y2Q5ODYwMjAxYjJjIiwidGFnIjoiIn0%3D',
                domain: 'tailwindui.com',
                path: '/',
                httpOnly: true,
                secure: true
            },
            {
                name: 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d',
                value: 'eyJpdiI6IlVxT01KRWo2VEFHQjhnYU5XZURwYmc9PSIsInZhbHVlIjoidUVhNlI0STVHSWI4RFR0L01oS1VDSmN4RnB2MWk0RmludEJzalNVNDZaaXJvM05yblBBRldzcDZxUkJvemh1V2RhT29kZUVrK3I1Mm42ZnVrdWlXaHh6djU1OXB1UkdqaEsrUTFic1lTQ0pMalhQbUJ3S25pbi9Fc3pDc3lYa2hmQlhtbTRTVHZKQ3BOR2p2N2I2eHZtYi9hS3Q2WmoyQmxja2daRm1zS3ZhSmsrYzhyZXdxYTJMNTJZTDk3TUVEeDVKRFpwSUlWcHpjYWFVc0Jwbk9xQm15MTUvYUNyc3dXVzRxOG9xWEpCcz0iLCJtYWMiOiI1YjA0NmIxYTM4OTgyOTI5ODg5MGQ0OTAyZTVhNzA2N2IzMTEwOTVmOGI5ZmY5MGMyMGQyZGQ4MjJiY2I1ZTg5IiwidGFnIjoiIn0%3D',
                domain: 'tailwindui.com',
                path: '/',
                httpOnly: true,
                secure: true
            },
            {
                name: 'XSRF-TOKEN',
                value: 'eyJpdiI6IlZHbnRLYitoUFNWQjh1d0lPSktid3c9PSIsInZhbHVlIjoiTWFDZFBpbFNYM2dEWnY2amREdUxXamVEQkRkOXlyQnJWSnEvUWZZUHRzcnRQWjEzbk1jOHBTbm5MQzJJUHRNOWk2Mk5VVHZERTdRSC85TVVoYm5zeFRaVGxYem5vcGNISHBzMmNFMFpVd3BoaktwTnBxdFJSZ1JBVkR4RHVxd0giLCJtYWMiOiIwZDAxYjY3ZmNmMmJhOTkzY2E3YzY2ZTI5N2ZjM2NmN2I1Zjc2ZmY0YzljNmJkZDEwYTY3Y2U2ZTA4ZDI1MjcwIiwidGFnIjoiIn0%3D',
                domain: 'tailwindui.com',
                path: '/',
                httpOnly: false,
                secure: true
            }
        );

        // Set headers
        await page.setExtraHTTPHeaders({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        });

        const visitedUrls = new Set<string>();
        const urlsToVisit = ["https://tailwindui.com/components"];

        while (urlsToVisit.length > 0) {
            const url = urlsToVisit.pop()!;
            if (visitedUrls.has(url)) continue;
            
            console.log(`\nVisiting: ${url}`);
            visitedUrls.add(url);

            try {
                await page.goto(url, { waitUntil: 'networkidle0' });

                // Wait for any of these selectors that might indicate the page is loaded
                await Promise.race([
                    page.waitForSelector('[role="tabpanel"]', { timeout: 10000 }),
                    page.waitForSelector('pre code', { timeout: 10000 }),
                    page.waitForSelector('iframe', { timeout: 10000 })
                ]).catch(() => console.log('Initial selector wait timed out, continuing...'));

                // Extract components from the page
                const components = await page.evaluate(() => {
                    const components: any[] = [];
                    
                    // Find all component sections using multiple possible selectors
                    const sections = Array.from(document.querySelectorAll('section'));
                    
                    sections.forEach((section) => {
                        const nameElement = section.querySelector('h2');
                        const name = nameElement?.textContent?.trim() || 'Unnamed Component';
                        
                        // Try to get code from different possible locations
                        const htmlCode = section.querySelector('iframe')?.srcdoc || '';
                        let reactCode = '';

                        // Try to get React code
                        const codeBlocks = section.querySelectorAll('pre code');
                        codeBlocks.forEach((block) => {
                            if (block.textContent?.includes('import') || block.textContent?.includes('export')) {
                                reactCode = block.textContent;
                            }
                        });

                        if (htmlCode || reactCode) {
                            components.push({
                                name,
                                url: window.location.href,
                                htmlCode,
                                reactCode,
                                timestamp: new Date().toISOString()
                            });
                        }
                    });

                    return components;
                });

                // Log what we found
                console.log(`Found ${components.length} components on ${url}`);

                // Save components
                for (const component of components) {
                    await saveComponent(component, outputDir);
                }

                // Find next pages to visit
                const newUrls = await page.evaluate(() => {
                    return Array.from(document.querySelectorAll('a[href*="/components"]'))
                        .map(a => a.href)
                        .filter(href => href.startsWith('https://tailwindui.com/components'));
                });

                urlsToVisit.push(...newUrls.filter(url => !visitedUrls.has(url)));

            } catch (error) {
                console.error(`Error processing ${url}:`, error);
            }
        }

        console.log(`\nScraped components from ${visitedUrls.size} pages`);

    } catch (error) {
        console.error("Scraping failed:", error);
    } finally {
        await browser.close();
    }
}

async function saveComponent(component: any, outputDir: string) {
    try {
        // Ensure output directory exists
        await mkdir(outputDir, { recursive: true });

        // Save to JSON file
        const jsonFile = Bun.file(outputDir + "/components.json");
        const existingData = await jsonFile.exists() ?
            JSON.parse(await jsonFile.text()) :
            [];

        existingData.push(component);
        await Bun.write(jsonFile, JSON.stringify(existingData, null, 2));

        // Save to TXT file for easier reading
        const txtContent = `
Component: ${component.name}
Source: ${component.url}
Timestamp: ${component.timestamp}

HTML Version:
${component.htmlCode || 'Not available'}

React Version:
${component.reactCode || 'Not available'}

----------------------------------------
`;

        const txtFile = Bun.file(outputDir + "/components.txt");
        const writer = txtFile.writer();
        writer.write(txtContent);
        await writer.flush();
        writer.end();

        console.log(`Saved component: ${component.name}`);
    } catch (error) {
        console.error('Error saving component:', error);
    }
}

// Run the scraper
scrapeUILibrary().catch(console.error);