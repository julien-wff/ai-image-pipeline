import { getContext, setContext } from 'svelte';
import { SvelteMap } from 'svelte/reactivity';

export interface Image {
    localFile: File | null;
    apiFile: ApiImage | null;
}

export type ImageStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ImageLabel = 'text' | 'painting' | 'photo' | 'sketch' | 'schematic';

export interface ApiImage {
    id: number;
    status: ImageStatus;
    uploaded_at: string;
    original_filename: string;
    upload_path: string;
    processed_path: string | null;
    processed_at: string | null;
    processing_time: number | null;
    error_message: string | null;
    label: ImageLabel | null;
    caption: string | null;
}

class AppState {
    #images = new SvelteMap<number, Image>();
    #uploadTaskCount = 0;

    get images() {
        return [ ...this.#images.values() ];
    }

    async fetchImages() {
        const response = await fetch('/api/images');
        for (const img of await response.json()) {
            this.#images.set(img.id, {
                localFile: null,
                apiFile: img,
            });
        }
    }

    async uploadImages(files: FileList) {
        this.#uploadTaskCount++;
        const newIDs = Array.from({ length: files.length }).map((_, i) => 1e8 + (this.#uploadTaskCount * 1000) + i);

        [ ...files ].forEach((file, i) => this.#images.set(newIDs[i], {
            localFile: file,
            apiFile: null,
        }));

        for (const id of newIDs) {
            const file = this.#images.get(id)!.localFile!;
            const body = new FormData();
            body.append('file', file);

            const res = await fetch('/api/images/upload', {
                method: 'POST',
                body,
            });
            const data: ApiImage = await res.json();

            this.#images.delete(id);
            this.#images.set(data.id, {
                localFile: file,
                apiFile: data,
            });
        }

        this.#uploadTaskCount--;
    }
}

const SYMBOL_KEY = 'app';

export function setAppState() {
    return setContext(Symbol.for(SYMBOL_KEY), new AppState());
}

export function useAppState() {
    return getContext<AppState>(Symbol.for(SYMBOL_KEY));
}
