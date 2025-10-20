import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [tailwindcss(), sveltekit()],
    server: {
        proxy: {
            '/api': 'http://localhost:8000',
            '/uploads': 'http://localhost:8000',
            '/processed': 'http://localhost:8000',
            '/docs': 'http://localhost:8000',
            '/openapi.json': 'http://localhost:8000',
        },
    },
});
