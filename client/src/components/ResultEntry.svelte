<script lang="ts">
	let {
		value = $bindable(),
		focusSubmit,
		disabled
	} = $props<{
		value: number;
		focusSubmit: () => void;
		disabled: boolean;
	}>();
	let inputRawValue = $state<string>('');
	let inputRef: HTMLInputElement;

	const DNF_KEYS = ['d', 'D', '/', '#'];
	const DNS_KEYS = ['s', 'S', '*'];

	const toInt = (input: string): number | null => {
		const int = parseInt(input);
		return isNaN(int) ? null : int;
	};

	const toCentiseconds = (input: string): number => {
		if (input === '') return 0;
		if (input === 'DNF') return -1;
		if (input === 'DNS') return -2;
		const num = toInt(input.replace(/\D/g, '')) || 0;
		return (
			Math.floor(num / 1000000) * 360000 +
			Math.floor((num % 1000000) / 10000) * 6000 +
			Math.floor((num % 10000) / 100) * 100 +
			(num % 100)
		);
	};

	const toClockFormat = (centiseconds: number): string => {
		if (centiseconds === -1) return 'DNF';
		if (centiseconds === -2) return 'DNS';
		if (!Number.isFinite(centiseconds)) {
			throw new Error(`Invalid centiseconds, expected positive number, got ${centiseconds}.`);
		}
		return new Date(centiseconds * 10)
			.toISOString()
			.substr(11, 11)
			.replace(/^[0:]*(?!\.)/g, '');
	};

	const reformatInput = (input: string): string => {
		const number = toInt(input.replace(/\D/g, '')) || 0;
		if (number === 0) return '';
		const str = '00000000' + number.toString().slice(0, 8);
		const match = str.match(/(\d\d)(\d\d)(\d\d)(\d\d)$/);
		if (!match) return '';
		const [, hh, mm, ss, cc] = match;
		return `${hh}:${mm}:${ss}.${cc}`.replace(/^[0:]*(?!\.)/g, '');
	};

	function handleInput(event: Event) {
		const inputElement = event.target as HTMLInputElement;
		const key = inputElement.value.slice(-1);

		if (DNF_KEYS.includes(key)) {
			inputRawValue = 'DNF';
			value = -1;
		} else if (DNS_KEYS.includes(key)) {
			inputRawValue = 'DNS';
			value = -2;
		} else {
			inputRawValue = reformatInput(inputElement.value);
			value = toCentiseconds(inputRawValue);
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		const inputs = document.querySelectorAll('input');
		const currentIndex = Array.from(inputs).indexOf(inputRef);
		const isLastInput = currentIndex === inputs.length - 1;

		if (
			event.key === 'ArrowUp' ||
			(event.key === 'Enter' && event.shiftKey) ||
			event.key === '-' ||
			event.key === 'NumpadSubtract'
		) {
			event.preventDefault();
			const prev = inputRef.closest('div')?.previousElementSibling?.querySelector('input');
			if (prev) prev.focus();
		} else if (
			event.key === 'ArrowDown' ||
			event.key === 'Enter' ||
			event.key === '+' ||
			event.key === 'NumpadAdd'
		) {
			event.preventDefault();
			if (isLastInput) {
				focusSubmit();
			} else {
				const next = inputRef.closest('div')?.nextElementSibling?.querySelector('input');
				if (next) next.focus();
			}
		}
	}

	function applyPlus2() {
		if (value >= 0) {
			value = value + 200;
			inputRawValue = toClockFormat(value);
		}
	}

	function setDNF() {
		value = -1;
		inputRawValue = 'DNF';
	}

	function setDNS() {
		value = -2;
		inputRawValue = 'DNS';
	}

	$effect(() => {
		if (value !== undefined) {
			inputRawValue = toClockFormat(value);
		}
	});
</script>

<input
	bind:this={inputRef}
	type="text"
	value={inputRawValue}
	oninput={handleInput}
	onkeydown={handleKeydown}
	class="h-12 rounded-md border-2 px-3 text-2xl {disabled
		? 'cursor-not-allowed bg-gray-200 text-gray-500'
		: ''}"
	{disabled}
/>
<button
	onclick={applyPlus2}
	onkeydown={handleKeydown}
	class="ml-1 h-12 rounded-md border-2 px-3 text-2xl hover:bg-gray-100 {disabled
		? 'cursor-not-allowed bg-gray-200 text-gray-500'
		: ''}"
	{disabled}
>
	+2
</button>
<button
	onclick={setDNF}
	onkeydown={handleKeydown}
	class="ml-1 h-12 rounded-md border-2 px-3 text-2xl hover:bg-gray-100 {disabled
		? 'cursor-not-allowed bg-gray-200 text-gray-500'
		: ''}"
	{disabled}
>
	DNF
</button>
<button
	onclick={setDNS}
	onkeydown={handleKeydown}
	class="ml-1 h-12 rounded-md border-2 px-3 text-2xl hover:bg-gray-100 {disabled
		? 'cursor-not-allowed bg-gray-200 text-gray-500'
		: ''}"
	{disabled}
>
	DNS
</button>

<!-- <span class="ml-1 text-2xl">{value}</span> -->
