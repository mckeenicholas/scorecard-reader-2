import { get, writable } from 'svelte/store';
import { goto } from '$app/navigation';

// Store for WCA authentication token and expiry
export const wcaToken = writable<string | null>(null);
export const wcaTokenExpiry = writable<Date | null>(null);
export const liveApiKey = writable<Map<string, string>>(new Map());

const links = {
	appId: 'r464RMsyf5jpnpz7xpBlQcrUU9gqjLN1336d0ucUxo0',
	redirect: 'http://localhost:5173'
};

/**
 * Initiates the login flow by redirecting to WCA OAuth.
 */
export const logIn = () => {
	window.location.href = `https://worldcubeassociation.org/oauth/authorize?client_id=${links.appId}&redirect_uri=${links.redirect}&response_type=token&scope=public+manage_competitions`;
};

/**
 * Handles the authentication response from WCA and updates the store.
 */
export const handleAuthRedirect = () => {
	if (window.location.hash) {
		const urlParams = new URLSearchParams(window.location.hash.substring(1));
		const accessToken = urlParams.get('access_token');
		const expiresIn = urlParams.get('expires_in');

		if (accessToken && expiresIn) {
			const currentTime = Math.floor(Date.now() / 1000);
			const expiry = new Date((currentTime + parseInt(expiresIn)) * 1000);

			wcaToken.set(accessToken);
			wcaTokenExpiry.set(expiry);

			// Redirect to home page after successful authentication
			goto('/home');
		}
	}
};

export const authFetch = async <T>(url: string | URL, options: RequestInit = {}) => {
	const token = get(wcaToken);
	const expiry = get(wcaTokenExpiry);

	if (!token || !expiry || expiry < new Date()) {
		goto('/');
		return;
	}

	// Merge headers with Authorization token
	const headers = {
		...options.headers,
		Authorization: `Bearer ${token}`,
		'Content-Type': 'application/json'
	};

	try {
		const response = await fetch(url, { ...options, headers });

		if (!response.ok) {
			throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
		}

		return (await response.json()) as T;
	} catch (error) {
		console.error('Failed to fetch:', error);
		throw error;
	}
};
