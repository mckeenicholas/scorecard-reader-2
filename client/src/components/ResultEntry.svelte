<script lang="ts">
	let { value } = $props<{ value: number }>();
	let inputRawValue = $state<string>('');

	const DNF_KEYS = ['d', 'D', '/', '#'];
	const DNS_KEYS = ['s', 'S', '*'];

	const toInt = (input: string) => {
		const int = parseInt(input);
		return isNaN(int) ? null : int;
	};

	const toCentiseconds = (input: string) => {
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

	const toClockFormat = (centiseconds: number) => {
		if (!Number.isFinite(centiseconds)) {
			throw new Error(`Invalid centiseconds, expected positive number, got ${centiseconds}.`);
		}
		return new Date(centiseconds * 10)
			.toISOString()
			.substr(11, 11)
			.replace(/^[0:]*(?!\.)/g, '');
	};

	const reformatInput = (input: string) => {
		const number = toInt(input.replace(/\D/g, '')) || 0;
		if (number === 0) return '';
		const str = '00000000' + number.toString().slice(0, 8);
		const [, hh, mm, ss, cc] = str.match(/(\d\d)(\d\d)(\d\d)(\d\d)$/);
		return `${hh}:${mm}:${ss}.${cc}`.replace(/^[0:]*(?!\.)/g, '');
	};

	const inputChange = (event) => {
		const key = event.key;

		if (DNF_KEYS.includes(key)) {
			inputRawValue = 'DNF';
		} else if (DNS_KEYS.includes(key)) {
			inputRawValue = 'DNS';
		} else {
			inputRawValue = reformatInput(event.target.value);
		}
	};

	const onBlur = () => {
		value = toCentiseconds(inputRawValue);
	};

	$effect(() => {
		inputRawValue = toClockFormat(value);
	});
</script>

<svelte:window onblur={onBlur} />
<input bind:value={inputRawValue} onchange={inputChange} />
