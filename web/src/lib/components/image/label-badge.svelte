<script lang="ts">
    import type { ImageLabel } from '$lib/stores/app.context.svelte';
    import { Badge } from '$lib/components/ui/badge/index.js';

    interface Props {
        label: ImageLabel;
        class?: string;
    }

    let { label, class: classNames }: Props = $props();

    const labels: Map<ImageLabel, { text: string, color: string }> = new Map([
        [ 'painting', { text: 'Painting', color: 'bg-blue-500 text-white' } ],
        [ 'sketch', { text: 'Sketch', color: 'bg-green-500 text-white' } ],
        [ 'photo', { text: 'Photo', color: 'bg-red-500 text-black' } ],
        [ 'schematic', { text: 'Schematic', color: 'bg-purple-500 text-white' } ],
        [ 'text', { text: 'Text', color: 'bg-yellow-500 text-white' } ],
    ]);
</script>

<Badge class="{classNames} {labels.get(label)?.color!}">
    {labels.get(label)?.text!}
</Badge>
