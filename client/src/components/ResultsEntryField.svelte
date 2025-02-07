<script lang="ts">
	import { getEventAttempts } from '../lib/utils';
	import ResultEntry from './ResultEntry.svelte';

	let { solveData = $bindable(), submitCallBack } = $props();

	let solveDataRepr = $state(solveData);

	let disabled = $state<boolean>(false);
	let submitButton: HTMLButtonElement;

	const attempts = getEventAttempts(solveData.event);

	function focusFirstInput() {
		const firstInput = document.querySelector('.my-2 input') as HTMLInputElement | null;
		if (firstInput) firstInput.focus();
	}

	function focusSubmit() {
		if (submitButton) submitButton.focus();
	}

	function handleSubmitKeydown(event: KeyboardEvent) {
		if (event.key === 'ArrowUp' || event.key === '-' || event.key === 'NumpadSubtract') {
			event.preventDefault();
			const inputs = document.querySelectorAll('input');
			const lastInput = inputs[inputs.length - 1];
			if (lastInput) lastInput.focus();
		}
	}

	const handleSubmit = async () => {
		disabled = true;
		await submitCallBack();
		disabled = false;

		setTimeout(() => {
			focusFirstInput();
		}, 0);
	};

	// This, and the template below is a really hacky workaround for Svelte not recognizing the two way binding since the
	// Outer object is const and the signal doesnt reach it or smth, idk.
	$effect(() => {
		solveData.time1 = solveDataRepr.time1;
		solveData.time2 = solveDataRepr.time2;
		solveData.time3 = solveDataRepr.time3;
		solveData.time4 = solveDataRepr.time4;
		solveData.time5 = solveDataRepr.time5;
	});
</script>

<div class="my-2">
	<ResultEntry bind:value={solveDataRepr.time1} {focusSubmit} {disabled} />
</div>
<div class="my-2">
	<ResultEntry bind:value={solveDataRepr.time2} {focusSubmit} {disabled} />
</div>
<div class="my-2">
	<ResultEntry bind:value={solveDataRepr.time3} {focusSubmit} {disabled} />
</div>
{#if attempts === 5}
	<div class="my-2">
		<ResultEntry bind:value={solveDataRepr.time4} {focusSubmit} {disabled} />
	</div>
	<div class="my-2">
		<ResultEntry bind:value={solveDataRepr.time5} {focusSubmit} {disabled} />
	</div>
{/if}

<button
	bind:this={submitButton}
	class="h-12 rounded-md border-2 px-3 text-2xl hover:bg-gray-100"
	onkeydown={handleSubmitKeydown}
	onclick={handleSubmit}
>
	Submit
</button>
