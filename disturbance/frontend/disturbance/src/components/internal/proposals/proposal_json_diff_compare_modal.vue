<template lang="html">
	<div id="proposal-json-diff-compare-modal">
		<modal transition="modal fade" title="Revision JSON Compare" :showOK="false" :showCancel="false" :force="true" :xxxlarge="true" @cancel="close">
			<div>
				<div class="row align-items-end mb-3">
					<div class="col-md-5">
						<label class="form-label" for="older-revision">Older revision</label>
						<select id="older-revision" v-model.number="olderVersion" class="form-select">
							<option v-for="revision in revisions" :key="`older-${revision.version}`" :value="revision.version">
								{{ revision.label }}
							</option>
						</select>
					</div>
                    <div class="col-md-5">
						<label class="form-label" for="newer-revision">Newer revision</label>
						<select id="newer-revision" v-model.number="newerVersion" class="form-select">
							<option v-for="revision in revisions" :key="`newer-${revision.version}`" :value="revision.version">
								{{ revision.label }}
							</option>
						</select>
					</div>
					<div class="col-md-2 d-grid">
						<span>
						<button class="btn btn-primary" :disabled="isComparing || !hasValidRevisionOrder" @click="compare">
							<i v-if="isComparing" class="fa fa-spinner fa-spin"></i>{{ isComparing ? 'Comparing...' : 'Compare' }}
						</button>
						</span>
					</div>
				</div>
				<div v-if="hasCompared" class="compare-label">
					<span class="compare-code compare-code-modify">Changed</span>
					<span class="compare-code compare-code-add">Added</span>
					<span class="compare-code compare-code-remove">Removed</span>
				</div>
				<div v-if="hasCompared" class="compare-toggle form-check form-switch">
					<input id="show-all-data-toggle" v-model="showAllData" class="form-check-input" type="checkbox">
					<label class="form-check-label" for="show-all-data-toggle">Show all data</label>
				</div>
				<div v-if="errorString" class="alert alert-danger">{{ errorString }}</div>
				<div v-else-if="hasCompared && diffRows.length" class="json-diff-layout">
					<section class="json-diff-panel">
						<header class="json-diff-panel-header">{{ revisionLabel(olderVersion) }}</header>
						<table class="table table-sm json-diff-table">
							<tbody ref="leftPane" @scroll="onPaneScroll('left')">
								<tr v-for="row in diffRows" :key="row.id">
									<td class="line-number">{{ displayLineNumber(row.left) }}</td>
									<td :class="lineClass(row.left)"><pre class="json-diff-line">{{ renderLine(row.left) }}</pre></td>
								</tr>
							</tbody>
					</table>
					</section>
					<section class="json-diff-panel">
						<header class="json-diff-panel-header">{{ revisionLabel(newerVersion) }}</header>
						<table class="table table-sm json-diff-table">
							<tbody ref="rightPane" @scroll="onPaneScroll('right')">
								<tr v-for="row in diffRows" :key="`${row.id}-older`">
									<td class="line-number">{{ displayLineNumber(row.right) }}</td>
									<td :class="lineClass(row.right)"><pre class="json-diff-line">{{ renderLine(row.right) }}</pre></td>
								</tr>
							</tbody>
						</table>
					</section>
				</div>
				<div v-else-if="hasCompared" class="alert alert-info mb-0">No JSON differences were found for these revisions.</div>
			</div>
			<template #footer>
				<button type="button" class="btn btn-secondary" @click="close">Close</button>
			</template>
		</modal>
	</div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import Differ from 'json-diff-kit/dist/differ'

export default {
	name: 'ProposalJsonDiffCompareModal',
	components: { modal },
	data: function() {
		return {
			isModalOpen: false,
			modelObject: null,
			historyContext: null,
			newerVersion: 0,
			olderVersion: 0,
			diffLeft: [],
			diffRight: [],
			errorString: '',
			hasCompared: false,
			isComparing: false,
			isSyncingScroll: false,
			showAllData: false,
		}
	},
	computed: {
		revisions: function() {
			// History keys are displayed in newest-to-oldest order and their array index
			// is the version accepted by the history-version API endpoint.
			if (!this.modelObject || !this.modelObject.reversion_history) {
				return []
			}
			// Sort the keys in descending order by date so the newest revision is first.
			return Object.keys(this.modelObject.reversion_history).map((id, version) => ({
				version,
				id,
				date: this.modelObject.reversion_history[id].date,
				label: `${id}: ${this.formatDate(this.modelObject.reversion_history[id].date)}`,
			}))
		},
		hasValidRevisionOrder: function() {
			// The newer revision must have a later lodgement date than the older revision.
			const newerRevision = this.revisions.find(revision => revision.version === this.newerVersion)
			const olderRevision = this.revisions.find(revision => revision.version === this.olderVersion)
			return Boolean(newerRevision && olderRevision && new Date(newerRevision.date) > new Date(olderRevision.date))
		},
		diffRows: function() {
			// json-diff-kit returns aligned lines for both sides. By default, omit
			// paired equal lines; the toggle exposes the complete JSON when needed.
			const rows = []
			const rowCount = Math.max(this.diffLeft.length, this.diffRight.length)
			for (let index = 0; index < rowCount; index++) {
				const left = this.diffLeft[index] || null
				const right = this.diffRight[index] || null
				const leftType = left && left.type ? left.type : 'equal'
				const rightType = right && right.type ? right.type : 'equal'
				if (!this.showAllData && leftType === 'equal' && rightType === 'equal') {
					continue
				}
				rows.push({ id: index, left, right })
			}
			return rows
		},
	},
	methods: {
		open: function({ modelObject, historyContext, olderVersion }) {
			// Reset all transient state so reopening the modal starts with selection,
			// rather than stale results from a previous comparison.
			this.modelObject = modelObject
			this.historyContext = historyContext
			this.newerVersion = 0
			this.olderVersion = olderVersion === undefined ? Math.min(1, this.revisions.length - 1) : olderVersion
			this.diffLeft = []
			this.diffRight = []
			this.errorString = ''
			this.hasCompared = false
			this.showAllData = false
			this.isModalOpen = true
		},
		close: function() {
			this.isModalOpen = false
		},
		compare: async function() {
			// Fetch only after both selections are confirmed; the API endpoint is expensive and can be slow for large JSON.
			if (!this.hasValidRevisionOrder) {
				this.errorString = 'The newer revision must have a later lodgement date than the older revision.'
				return
			}
			this.isComparing = true
			this.errorString = ''
			try {
				// Fetch both revisions in parallel, then diff them. The API endpoint returns the full JSON for each revision.
				const [newerData, olderData] = await Promise.all([
					this.fetchVersion(this.newerVersion),
					this.fetchVersion(this.olderVersion),
				])
				// Use json-diff-kit to produce aligned lines for both sides, including modifications, additions, and removals.
				const differ = new Differ({ detectCircular: false, maxDepth: Infinity, arrayDiffMethod: 'lcs', showModifications: true, ignoreCase: false, preserveKeyOrder: 'before' })
				// Normalise the JSON to avoid false positives from differences in whitespace or key order.
				const diff = differ.diff(this.normaliseJson(olderData), this.normaliseJson(newerData))
				this.diffLeft = diff[0]
				this.diffRight = diff[1]
				this.hasCompared = true
				this.$nextTick(() => this.syncRowHeights())
			} catch (error) {
				this.diffLeft = []
				this.diffRight = []
				this.hasCompared = false
				this.errorString = error && error.message ? error.message : 'Unable to load the selected revisions.'
			} finally {
				this.isComparing = false
			}
		},
		fetchVersion: async function(version) {
			// Use the supplied history context so this reusable modal addresses the
			// matching serializer and model route for the current revision history.
			const url = '/api/history/version/' +
            this.historyContext.app_label + '/' +
			this.historyContext.component_name + '/' +
            this.historyContext.model_name + '/' +
            this.historyContext.serializer_name + '/' +
            this.modelObject.id + '/' +
            version + '/' +
            '?compare_fields_only=true';
			
			const response = await fetch(url)
			if (!response.ok) {
				const error = await response.json()
				throw new Error(error.detail || 'Unable to load revision data.')
			}
			return response.json()
		},
		normaliseJson: function(data) {
			return JSON.parse(JSON.stringify(data || null))
		},
		revisionLabel: function(version) {
			const revision = this.revisions.find(item => item.version === version)
			return revision ? revision.label : ''
		},
		formatDate: function(data) {
			return data ? moment(data).format('DD/MM/YYYY HH:mm:ss') : 'Draft'
		},
		
		// this return array of classes for the line, based on the type of change (added, removed, modified, equal)
		lineClass: function(line) { 
			// The line type is used to style the background of the cell to indicate whether it was added, removed, or modified.
			return ['json-diff-cell', `json-diff-cell-${line && line.type ? line.type : 'equal'}`] 
		},
		// this returns the line number for the line, or an empty string if there is no line number
		displayLineNumber: function(line) {
			return line && line.lineNumber ? line.lineNumber : ''
		},
		// this adds indentation to the line text based on the level of nesting in the JSON structure, 
		// and appends a comma if the line is not the last item in an object or array
		renderLine: function(line) {
			return line ? `${'  '.repeat(line.level || 0)}${line.text}${line.comma ? ',' : ''}` : ''
		},
		onPaneScroll: function(sourcePane) {
			// Keep aligned diff rows visible together while preventing recursive scroll events.
			if (this.isSyncingScroll) return
			const source = this.$refs[sourcePane === 'left' ? 'leftPane' : 'rightPane']
			const target = this.$refs[sourcePane === 'left' ? 'rightPane' : 'leftPane']
			if (!source || !target) return
			this.isSyncingScroll = true
			target.scrollTop = source.scrollTop
			requestAnimationFrame(() => { this.isSyncingScroll = false })
		},
		syncRowHeights: function() {
			// Wrapped JSON lines can differ in height; use the tallest side for each pair.
			const leftRows = this.$refs.leftPane ? this.$refs.leftPane.querySelectorAll('tr') : []
			const rightRows = this.$refs.rightPane ? this.$refs.rightPane.querySelectorAll('tr') : []
			for (let index = 0; index < Math.max(leftRows.length, rightRows.length); index++) {
				const height = Math.max(leftRows[index] ? leftRows[index].offsetHeight : 0, rightRows[index] ? rightRows[index].offsetHeight : 0)
				if (leftRows[index]) leftRows[index].style.height = `${height}px`
				if (rightRows[index]) rightRows[index].style.height = `${height}px`
			}
		},
	},
}
</script>

<style scoped>
.compare-label { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.compare-toggle { margin-bottom: 12px; color: #4b5563; }
.compare-code { border-radius: 555px; padding: 4px 10px; font-size: 0.8rem; font-weight: 600; }
.compare-code-modify { background: #fff7e6;  }
.compare-code-add { background: #edf7ea; }
.compare-code-remove { background: #fceeee;}
.json-diff-layout { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.json-diff-panel { overflow: hidden; min-width: 0; border: 1px solid #e5e7eb; border-radius: 8px; }
.json-diff-panel-header { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; background: #f9fafb; font-weight: 700; }
.json-diff-table { margin-bottom: 0; table-layout: fixed; }
.json-diff-table tbody { display: block; max-height: 60vh; overflow: auto; }
.json-diff-table tr { display: table; width: 100%; table-layout: fixed; }
.line-number { width: 64px; background: #fafafa; color: #9ca3af; font-family: monospace; text-align: right; vertical-align: top; }
.json-diff-cell { padding: 0; vertical-align: top; }
.json-diff-cell-modify { background: #fffdf2; }
.json-diff-cell-add { background: #f5fbf2; }
.json-diff-cell-remove { background: #fff4f4; }
.json-diff-line { margin: 0; padding: 6px 10px; white-space: pre-wrap; word-break: break-word; font-family: monospace; font-size: 0.82rem; line-height: 1.45; background: transparent; border: 0; }
</style>
