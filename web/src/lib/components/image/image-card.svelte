<script lang="ts">
    import { type Image, useAppState } from '$lib/stores/app.context.svelte';
    import * as Card from '$lib/components/ui/card';
    import * as ContextMenu from '$lib/components/ui/context-menu';
    import { Tween } from 'svelte/motion';
    import { cubicInOut } from 'svelte/easing';
    import { fade } from 'svelte/transition';
    import LabelBadge from '$lib/components/image/label-badge.svelte';
    import Trash2 from '@lucide/svelte/icons/trash-2';

    interface Props {
        image: Image;
    }

    let { image }: Props = $props();

    const state = useAppState();

    const imageURL = $derived(
        image.apiFile?.processed_path
        || image.apiFile?.upload_path
        || (image.localFile && URL.createObjectURL(image.localFile)),
    );

    let progress = new Tween(0, {
        duration: 300,
        easing: cubicInOut,
    });

    $effect(() => {
        progress.target = image.progress ?? 0;
    });
</script>

<style>
    progress::-webkit-progress-bar, progress::-moz-progress-bar {
        background-color: var(--primary);
    }
</style>

<ContextMenu.Root>
    <ContextMenu.Trigger>
        <Card.Root class="w-54 py-0 pb-2 overflow-clip gap-2">
            <div class="relative w-full h-54 aspect-square">
                <img class="w-full h-full object-cover" src={imageURL} alt="Upload"/>

                {#if image.apiFile?.label}
                    <div in:fade={{duration: 200}}>
                        <LabelBadge label={image.apiFile.label} class="absolute top-2 right-2"/>
                    </div>
                {/if}

                {#if image.apiFile?.status !== 'completed'}
                    <progress class="absolute left-0 bottom-0 w-full"
                              value={progress.current}
                              out:fade={{duration: 200}}
                              max="1"></progress>
                {/if}
            </div>

            <Card.Content class="px-2 line-clamp-1">
                {image.message || image.apiFile?.status || 'Uploading...'}
            </Card.Content>
        </Card.Root>
    </ContextMenu.Trigger>
    <ContextMenu.Content>
        <ContextMenu.Item disabled={!image.apiFile?.id}
                          onclick={() => state.deleteImage(image.apiFile!.id)}
                          variant="destructive">
            <Trash2 class="w-4 h-4"/>
            Delete
        </ContextMenu.Item>
    </ContextMenu.Content>
</ContextMenu.Root>
