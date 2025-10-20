<script lang="ts">
    import { useAppState } from '$lib/stores/app.context.svelte';

    const state = useAppState();
</script>

<pre><code>{JSON.stringify(state.images, null, 2)}</code></pre>
