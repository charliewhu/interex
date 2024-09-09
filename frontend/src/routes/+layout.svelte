<script lang="ts">
	import '../app.css'
	import { ModeWatcher } from 'mode-watcher'

	let { children } = $props()
</script>

<main class="container mx-auto max-w-3xl py-10">
	{@render children()}
	<ModeWatcher />
</main>
