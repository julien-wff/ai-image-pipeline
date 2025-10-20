<script lang="ts">
    import '../app.css';
    import favicon from '$lib/assets/favicon.svg';
    import * as Sidebar from '$lib/components/ui/sidebar';
    import AppSidebar from '$lib/components/sidebar/app-sidebar.svelte';
    import { setAppState } from '$lib/stores/app.context.svelte';

    let { children } = $props();

    const state = setAppState();
    state.fetchImages();
</script>

<svelte:head>
    <link rel="icon" href={favicon}/>
    <title>AI Image Pipeline</title>
</svelte:head>

<Sidebar.Provider>
    <AppSidebar/>
    <main>
        {@render children?.()}
    </main>
</Sidebar.Provider>
