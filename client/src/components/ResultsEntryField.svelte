<script lang="ts">
	import { getEventAttempts } from '../lib/utils';
	import ResultEntry from './ResultEntry.svelte';

	const { solveData } = $props();

	const attempts = getEventAttempts(solveData.event);
</script>

{#each range(attempts) as attemptNum}
	<div class="mx-2">
		<ResultEntry bind:value={solveData[attemptNum]} />
	</div>
{/each}
