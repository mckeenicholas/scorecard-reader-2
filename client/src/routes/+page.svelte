<script lang="ts">
	import { onMount } from 'svelte';
	import { logIn, handleAuthRedirect } from '../stores/wcaStore';

	onMount(() => {
		handleAuthRedirect();
	});
</script>

<button class="m-4 rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600" on:click={logIn}>
	Log in with WCA
</button>
