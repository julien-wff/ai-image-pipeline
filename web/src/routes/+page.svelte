<script lang="ts">
    import { useAppState } from '$lib/stores/app.context.svelte';
    import ImageCard from '$lib/components/image/image-card.svelte';
    import { onMount } from 'svelte';

    const state = useAppState();

    onMount(() => {
        return state.subscribe();
    });
</script>

<div class="p-4 flex gap-4 flex-wrap">
    {#each state.images as image}
        <ImageCard {image}/>
    {/each}
</div>
