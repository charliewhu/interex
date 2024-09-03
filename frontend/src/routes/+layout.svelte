<script lang="ts">
	import '../app.css'

	let { children } = $props()
</script>

<main class="container mx-auto pt-8 prose">
	{@render children()}
</main>
