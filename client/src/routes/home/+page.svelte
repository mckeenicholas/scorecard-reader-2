<script lang="ts">
	import { onMount } from 'svelte';
	import { authFetch } from '../../stores/wcaStore';
	import type { Competition } from '$lib/types';

	let competitions = $state<Competition[]>([]);
	let error = $state<boolean>(false);

	const oneWeekAgo = new Date(Date.now() - 2 * 7 * 24 * 60 * 60 * 1000);
	const params = new URLSearchParams({
		managed_by_me: 'true',
		start: oneWeekAgo.toISOString()
	});

	const fetchCompetitions = async () => {
		const response = await authFetch<Competition[]>(
			`https://www.worldcubeassociation.org/api/v0/competitions?${params.toString()}`
		);

		if (!response) {
			error = true;
			return;
		}

		competitions = response.sort(
			(a, b) => new Date(a.start_date).getTime() - new Date(b.start_date).getTime()
		);
	};

	onMount(() => {
		fetchCompetitions();
	});
</script>

<div class="m-4">
	{#if error}
		<p>Error fetching data</p>
	{:else}
		<ul>
			{#each competitions as competition}
				<li class="pb-2">
					<a
						href={`competition/${competition.id}`}
						class="text-blue-600 underline hover:text-blue-400"
					>
						{competition.name}
					</a>
				</li>
			{/each}
		</ul>
	{/if}
</div>
