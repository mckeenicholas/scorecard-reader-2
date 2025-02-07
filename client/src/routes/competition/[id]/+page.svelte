<script lang="ts">
	import { page } from '$app/stores';
	import { idToEventName, submitWCALiveResults, type ScannedResult } from '$lib/utils';
	import ResultsEntryField from '../../../components/ResultsEntryField.svelte';
	import { liveApiKey, wcaToken } from '../../../stores/wcaStore';
	import { get } from 'svelte/store';

	const compId = $page.params.id;

	let hasKey = $state<boolean>(false);
	let apiKeyInput = $state<string>('');
	let files = $state<any[]>([]);
	let message = $state<string>('');
	let results = $state<any[]>([]); // Store results data
	let currentResult = $state<ScannedResult | null>(null); // Store next result
	let showModal = $state<boolean>(false); // Control modal visibility
	let loading = $state<boolean>(false);
	let noResultsMessage = $state<string>(''); // Message for no results
	let showManualQueryButton = $state<boolean>(false); // Control visibility of manual query button

	let resultImageURL = $derived(
		currentResult ? `http://localhost:8000/images/${currentResult.id}.jpg` : ''
	);

	let apiKey = '';

	$effect(() => {
		console.log(currentResult);
	});

	liveApiKey.subscribe((map) => {
		if (map.has(compId)) {
			apiKey = map.get(compId) || '';
			hasKey = true;
		}
	});

	const saveKey = () => {
		if (apiKeyInput !== '') {
			get(liveApiKey).set(compId, apiKeyInput);
			hasKey = true;
		}
	};

	const uploadFiles = async () => {
		if (!files.length) {
			message = 'Please select files to upload.';
			return;
		}

		const formData = new FormData();
		for (const file of files) {
			formData.append('images', file);
		}

		loading = true;

		try {
			const response = await fetch('http://localhost:8000/upload', {
				method: 'POST',
				body: formData
			});

			if (response.ok) {
				message = 'Upload successful!';
				// After upload, automatically fetch the next result
				await getNextResult();
			} else {
				message = 'Upload failed. Please try again.';
			}
		} catch (error) {
			console.error('Error uploading files:', error);
			message = 'An error occurred while uploading.';
		}

		loading = false;
	};

	const getNextResult = async () => {
		currentResult = null;

		const res = await fetch('http://localhost:8000/next');
		const data = await res.json();

		if (data.message === 'No more results available.') {
			noResultsMessage = data.message; // Set message if no result
			showManualQueryButton = true; // Show manual query button
			currentResult = null; // Clear the next result
		} else {
			currentResult = data; // Show the next result
			showManualQueryButton = false; // Hide manual query button
		}
	};

	const updateResult = async () => {
		if (!currentResult || !currentResult.id) {
			console.error('Invalid result ID');
			return;
		}

		try {
			const res = await fetch('http://localhost:8000/result/update', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ submitted: currentResult.id })
			});

			const data = await res.json();
			if (!res.ok) {
				throw new Error(data.detail || 'Failed to update result');
			}

			console.log('Result updated successfully:', data);
		} catch (error) {
			console.error('Error updating result:', error.message);
		}
	};

	const getResults = async () => {
		const res = await fetch('http://localhost:8000/all');
		const data = await res.json();

		results = data; // Store results in state
		showModal = true; // Show modal with results
	};

	const closeModal = () => {
		showModal = false; // Close modal
	};

	const manualQuery = async () => {
		await getNextResult();
	};

	const submit = async () => {
		if (currentResult) {
			const wcaLiveAPIKey = get(liveApiKey);
			await submitWCALiveResults(compId, wcaLiveAPIKey, currentResult);
			await updateResult();
			await getNextResult();
		}
	};
</script>

<main class="flex flex-col items-center gap-4 p-10">
	{#if hasKey}
		<div class="flex">
			<input
				type="file"
				accept="image/*"
				multiple
				onchange={(e) => (files = Array.from(e.target.files))}
			/>
			<button class="bg-slate rounded-md border-2 p-2 hover:bg-gray-100" onclick={uploadFiles}
				>Upload</button
			>
			<button onclick={getResults} class="bg-slate ms-2 rounded-md border-2 p-2 hover:bg-gray-100"
				>View All Results</button
			>
			<button
				onclick={getNextResult}
				class="bg-slate ms-2 rounded-md border-2 p-2 hover:bg-gray-100">View Next Result</button
			>
		</div>
		<p>{message}</p>
		{#if loading}<p>Processing results, please wait...</p>{/if}

		{#if showModal}
			<div class="fixed inset-0 flex items-center justify-center bg-gray-500 bg-opacity-75">
				<div class="w-96 rounded-lg bg-white p-4">
					<h2 class="mb-2 text-xl">All Results</h2>
					<ul>
						{#each results as result}
							<li>
								<strong>CompetitorID:</strong>
								{result.competitorID} | <strong>Round:</strong>
								{result.round} | <strong>Event:</strong>
								{idToEventName(result.event)}
							</li>
						{/each}
					</ul>
					<button class="mt-2 rounded bg-red-500 p-2 text-white" onclick={closeModal}>Close</button>
				</div>
			</div>
		{/if}

		{#if currentResult}
			<!-- svelte-ignore a11y_missing_attribute -->
			<div class="flex flex-row items-center justify-center space-x-8">
				<div class="flex flex-col items-center">
					<img src={resultImageURL} class="max-h-[650px] object-contain" />
				</div>

				<div class="flex flex-col items-start">
					<div class="mt-8">
						<div class="my-10">
							<p class="text-xl"><strong>Competitor ID:</strong> {currentResult.competitorID}</p>
							<p class="text-xl"><strong>Round:</strong> {currentResult.round}</p>
							<p class="text-xl"><strong>Event:</strong> {idToEventName(currentResult.event)}</p>
						</div>
						<ResultsEntryField bind:solveData={currentResult} submitCallBack={submit} />
					</div>
				</div>
			</div>
		{/if}

		{#if noResultsMessage}
			<p>{noResultsMessage}</p>
			{#if showManualQueryButton}
				<button class="bg-slate rounded-md border-2 p-2 hover:bg-gray-100" onclick={manualQuery}
					>Manually Fetch Next Result</button
				>
			{/if}
		{/if}
	{:else}
		<p>Please enter your WCA Live API Key</p>
		<input type="password" bind:value={apiKeyInput} class="bg-slate rounded-md border-2 text-2xl" />
		<button onclick={saveKey} class="bg-slate rounded-md border-2 p-2 hover:bg-gray-100"
			>Enter</button
		>
	{/if}
</main>
