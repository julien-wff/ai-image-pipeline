<script lang="ts">
    import * as Sidebar from '$lib/components/ui/sidebar';
    import { Button } from '$lib/components/ui/button';
    import UploadIcon from '@lucide/svelte/icons/upload';
    import { useAppState } from '$lib/stores/app.context.svelte';

    let fileInput: HTMLInputElement;
    const state = useAppState();

    function handleUploadBtnClick() {
        fileInput.click();
    }

    function handleFileChange(event: Event) {
        const files = fileInput.files;
        if (files) {
            state.uploadImages(files);
        }
    }
</script>

<Sidebar.Footer>
    <input id="file-upload"
           type="file"
           multiple
           accept=".jpg,.jpeg,.png"
           class="hidden"
           onchange={handleFileChange}
           bind:this={fileInput}/>

    <label for="file-upload" class="w-full">
        <Button class="w-full justify-start h-8" size="sm" variant="default" onclick={handleUploadBtnClick}>
            <UploadIcon class="mr-2 h-4 w-4"/>
            Upload images
        </Button>
    </label>
</Sidebar.Footer>
