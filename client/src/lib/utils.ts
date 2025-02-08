const STAGING = import.meta.env.VITE_STAGING === 'true';

export const eventNames: { [key: string]: string } = {
	'333': '3x3x3 Cube',
	'222': '2x2x2 Cube',
	'444': '4x4x4 Cube',
	'555': '5x5x5 Cube',
	'666': '6x6x6 Cube',
	'777': '7x7x7 Cube',
	'333bf': '3x3x3 Blindfolded',
	'333fm': '3x3x3 Fewest Moves',
	'333oh': '3x3x3 One-Handed',
	minx: 'Megaminx',
	pyram: 'Pyraminx',
	clock: 'Clock',
	skewb: 'Skewb',
	sq1: 'Square-1',
	'444bf': '4x4x4 Blindfolded',
	'555bf': '5x5x5 Blindfolded',
	'333mbf': '3x3x3 Multi-Blind'
};

export type SupportedWCAEvent =
	| '222'
	| '333'
	| '444'
	| '555'
	| '666'
	| '777'
	| '333bf'
	| '333fm'
	| '333oh'
	| 'minx'
	| 'pyram'
	| 'clock'
	| 'skewb'
	| 'sq1'
	| '444bf'
	| '555bf';

export const eventInfo: Record<SupportedWCAEvent, { attempts: number; format: string }> = {
	333: { attempts: 5, format: 'a' },
	222: { attempts: 5, format: 'a' },
	444: { attempts: 5, format: 'a' },
	555: { attempts: 5, format: 'a' },
	666: { attempts: 3, format: 'm' },
	777: { attempts: 3, format: 'm' },
	'333bf': { attempts: 3, format: 'b' },
	'333fm': { attempts: 3, format: 'm' },
	'333oh': { attempts: 5, format: 'a' },
	minx: { attempts: 5, format: 'a' },
	pyram: { attempts: 5, format: 'a' },
	clock: { attempts: 5, format: 'a' },
	skewb: { attempts: 5, format: 'a' },
	sq1: { attempts: 5, format: 'a' },
	'444bf': { attempts: 3, format: 'b' },
	'555bf': { attempts: 3, format: 'b' }
};

export type StatusType = 'scanned' | 'submitted' | 'doublechecked';

export interface ScannedResult {
	id: number;
	competitorID: number;
	round: number;
	event: SupportedWCAEvent;
	time1: number;
	time2: number;
	time3: number;
	time4: number;
	time5: number;
	time6: number;
	status: StatusType;
}

export const getEventAttempts = (event: SupportedWCAEvent) => {
	return eventInfo[event].attempts;
};

export const submitWCALiveResults = async (
	compId: string,
	token: string,
	result: ScannedResult
) => {
	const resultSubmitObject = {
		competitionWcaId: compId,
		eventId: result.event,
		roundNumber: result.round,
		results: [
			{
				registrantId: result.competitorID,
				attempts: [
					{ result: result.time1 },
					{ result: result.time2 },
					{ result: result.time3 },
					{ result: result.time4 },
					{ result: result.time5 }
				]
			}
		]
	};

	if (STAGING) {
		console.log(resultSubmitObject);
		return;
	}

	const response = await fetch('https://live.worldcubeassociation.org/api/enter-results', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(resultSubmitObject)
	});

	if (!response.ok) {
		throw new Error(`Failed to submit result: ${response.statusText}`);
	}

	return await response.json();
};

export const idToEventName = (id: SupportedWCAEvent) => {
	return eventNames[id];
};
