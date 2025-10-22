<script lang="ts">
    import UploadIcon from '@lucide/svelte/icons/upload';
    import SearchIcon from '@lucide/svelte/icons/search';
    import Loader2Icon from '@lucide/svelte/icons/loader-2';
    import CheckCircleIcon from '@lucide/svelte/icons/check-circle';
    import ImageIcon from '@lucide/svelte/icons/image';
    import WorkflowIcon from '@lucide/svelte/icons/workflow';
    import FileTextIcon from '@lucide/svelte/icons/file-text';
    import PaletteIcon from '@lucide/svelte/icons/palette';
    import * as Sidebar from '$lib/components/ui/sidebar';
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import { Separator } from '$lib/components/ui/separator';
    import SidebarFooter from '$lib/components/sidebar/sidebar-footer.svelte';

    const navData = [
        {
            title: 'Status',
            icon: CheckCircleIcon,
            items: [
                {
                    title: 'Processing',
                    isActive: false,
                },
                {
                    title: 'Done',
                    isActive: false,
                },
            ],
        },
        {
            title: 'Labels',
            icon: FileTextIcon,
            items: [
                {
                    title: 'All',
                    isActive: true,
                },
                {
                    title: 'Photos only',
                    isActive: false,
                },
            ],
        }
    ];
</script>

<Sidebar.Root>
    <Sidebar.Header>
        <Sidebar.Menu>
            <Sidebar.MenuItem>
                <Sidebar.MenuButton size="lg">
                    {#snippet child({ props })}
                        <a href="/" {...props}>
                            <div class="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                                <ImageIcon class="size-4"/>
                            </div>
                            <div class="flex flex-col gap-0.5 leading-none">
                                <span class="font-semibold">AI Image Pipeline</span>
                            </div>
                        </a>
                    {/snippet}
                </Sidebar.MenuButton>
            </Sidebar.MenuItem>
        </Sidebar.Menu>
    </Sidebar.Header>

    <Sidebar.Content>
        <Sidebar.Group>
            <Sidebar.Menu>
                {#each navData as item (item.title)}
                    <Sidebar.MenuItem class="mb-4">
                        <Sidebar.MenuButton class="font-medium">
                            {#snippet child({ props })}
                                <div {...props}>
                                    <item.icon/>
                                    <span class="font-semibold">{item.title}</span>
                                </div>
                            {/snippet}
                        </Sidebar.MenuButton>
                        {#if item.items?.length}
                            <Sidebar.MenuSub>
                                {#each item.items as subItem (subItem.title)}
                                    <Sidebar.MenuSubItem>
                                        <Sidebar.MenuSubButton isActive={subItem.isActive}>
                                            {#snippet child({ props })}
                                                <span {...props}>{subItem.title}</span>
                                            {/snippet}
                                        </Sidebar.MenuSubButton>
                                    </Sidebar.MenuSubItem>
                                {/each}
                            </Sidebar.MenuSub>
                        {/if}
                    </Sidebar.MenuItem>
                {/each}
            </Sidebar.Menu>
        </Sidebar.Group>
    </Sidebar.Content>

    <SidebarFooter/>

    <Sidebar.Rail/>
</Sidebar.Root>
