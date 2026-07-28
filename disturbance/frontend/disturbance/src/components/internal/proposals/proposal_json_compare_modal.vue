<template lang="html">
    <div id="proposal-json-compare-modal">
        <modal transition="modal fade" :title="title" :showOK="false" :showCancel="false" :force="true" :xxlarge="true" @cancel="cancel">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-sm-12">
                        <div class="compare-summary">
                            <span class="compare-badge compare-badge-current">{{ leftLabel }}</span>
                            <span class="compare-summary-text">compared with</span>
                            <span class="compare-badge compare-badge-previous">{{ rightLabel }}</span>
                        </div>
                        <div class="compare-legend">
                            <span class="legend-chip legend-chip-modify">Changed</span>
                            <span class="legend-chip legend-chip-add">Added</span>
                            <span class="legend-chip legend-chip-remove">Removed</span>
                        </div>
                        <div class="compare-toggle form-check form-switch">
                            <input id="show-all-data-toggle" v-model="showAllData" class="form-check-input" type="checkbox">
                            <label class="form-check-label" for="show-all-data-toggle">Show all data</label>
                        </div>
                        <div v-if="errorString" class="alert alert-danger">
                            {{ errorString }}
                        </div>
                        <div v-else-if="diffRows.length" class="json-diff-layout">
                            <section class="json-diff-panel">
                                <header class="json-diff-panel-header">{{ leftHeading }}</header>
                                <table class="table table-sm json-diff-table">
                                    <tbody ref="leftPane" @scroll="onPaneScroll('left')">
                                        <tr v-for="row in diffRows" :key="row.id">
                                            <td class="line-number-cell">{{ lineNumberText(row.left) }}</td>
                                            <td :class="lineClass(row.left)">
                                                <pre class="json-diff-line">{{ renderLine(row.left) }}</pre>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </section>
                            <section class="json-diff-panel">
                                <header class="json-diff-panel-header">{{ rightHeading }}</header>
                                <table class="table table-sm json-diff-table">
                                    <tbody ref="rightPane" @scroll="onPaneScroll('right')">
                                        <tr v-for="row in diffRows" :key="`${row.id}-right`">
                                            <td class="line-number-cell">{{ lineNumberText(row.right) }}</td>
                                            <td :class="lineClass(row.right)">
                                                <pre class="json-diff-line">{{ renderLine(row.right) }}</pre>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </section>
                        </div>
                        <div v-else class="alert alert-info mb-0">
                            No JSON differences were found for these revisions.
                        </div>
                    </div>
                </div>
            </div>
            <template #footer>
                <button type="button" class="btn btn-secondary" @click="cancel">Close</button>
            </template>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import Differ from 'json-diff-kit/dist/differ'

export default {
    name: 'ProposalJsonCompareModal',
    components: {
        modal,
    },
    data: function() {
        return {
            isModalOpen: false,
            errorString: '',
            leftHeading: 'Newer Version',
            rightHeading: 'Older Version',
            leftLabel: '',
            rightLabel: '',
            diffLeft: [],
            diffRight: [],
            isSyncingScroll: false,
            showAllData: false,
        }
    },
    computed: {
        title: function() {
            return 'Revision JSON Compare';
        },
        // Compute the rows to display in the diff tables, filtering out equal lines if showAllData is false.
        diffRows: function() {
            const rows = [];
            const rowCount = Math.max(this.diffLeft.length, this.diffRight.length);
            for (let index = 0; index < rowCount; index++) {
                const left = this.diffLeft[index] || null;
                const right = this.diffRight[index] || null;
                const leftType = left && left.type ? left.type : 'equal';
                const rightType = right && right.type ? right.type : 'equal';

                // If showAllData is false and both left and right lines are equal, skip this row.
                if (!this.showAllData && leftType === 'equal' && rightType === 'equal') {
                    continue;
                }
                // Add the row to the list of rows to display.
                rows.push({
                    id: index,
                    left,
                    right,
                });
            }
            return rows;
        },
    },
    watch: {
    },
    methods: {
        open: function({ newerVersion, olderVersion, lodgementNumber, reversionHistoryLength, newerDate, olderDate, newerData, olderData }) {
            try {
                const differ = new Differ({
                    detectCircular: false,
                    maxDepth: Infinity,
                    arrayDiffMethod: 'lcs',
                    showModifications: true,
                    ignoreCase: false,
                    preserveKeyOrder: 'before',
                });
                // Build one diff object and pass it straight through to the viewer props.
                const diff = differ.diff(this.normaliseJson(newerData), this.normaliseJson(olderData));
                this.diffLeft = diff[0];
                this.diffRight = diff[1];
                this.leftHeading = this.buildHeading('Current Revision', newerVersion, newerDate);
                this.rightHeading = this.buildHeading('Compared Revision', olderVersion, olderDate);
                this.leftLabel = this.buildRevisionLabel(lodgementNumber, reversionHistoryLength, newerVersion, newerDate);
                this.rightLabel = this.buildRevisionLabel(lodgementNumber, reversionHistoryLength, olderVersion, olderDate);
                this.errorString = '';
                this.isModalOpen = true;
                this.$nextTick(() => {
                    this.resetPaneScrollPosition();
                    this.syncRowHeights();
                });

            } catch (error) {
                this.diffLeft = [];
                this.diffRight = [];
                this.errorString = error && error.message ? error.message : 'Unable to generate the JSON diff.';
                this.isModalOpen = true;
                this.$nextTick(() => {
                    this.resetPaneScrollPosition();
                    this.syncRowHeights();
                });

            }
        },
        cancel: function() {
            this.close();
        },
        close: function() {
            this.isModalOpen = false;
            this.errorString = '';
            this.diffLeft = [];
            this.diffRight = [];
            this.isSyncingScroll = false;
        },
        // Normalise the JSON data by stringifying and parsing it, which removes any undefined values and ensures consistent formatting.
        normaliseJson: function(data) {
            return JSON.parse(JSON.stringify(data || null));
        },
        // Build a heading for the revision, including the prefix, version number, and formatted lodgement date.
        buildHeading: function(prefix, version, lodgementDate) {
            if (version === 0) {
                return `${prefix} (${this.formatDate(lodgementDate)})`;
            }
            return `${prefix} (${version} older, ${this.formatDate(lodgementDate)})`;
        },
        // Build a label for the revision, including the lodgement number, revision number, and formatted lodgement date.
        buildRevisionLabel: function(lodgementNumber, reversionHistoryLength, version, lodgementDate) {
            const revisionNumber = reversionHistoryLength - version;
            return `${lodgementNumber}-${revisionNumber}: ${this.formatDate(lodgementDate)}`;
        },
        // Format a date string into a more human-readable format, or return a default message if the date is null or undefined.
        formatDate: function(data) {
            return data ? moment(data).format('MMMM Do YYYY') + ' at ' + moment(data).format('h:mm:ss a') : 'Draft just prior to lodgement.';
        },
        // Determine the CSS class for a given line object based on its type (equal, modify, add, remove).
        lineClass: function(line) {
            const type = line && line.type ? line.type : 'equal';
            return [
                'json-diff-cell',
                `json-diff-cell-${type}`,
            ];
        },
        // Get the line number text for a given line object, or return an empty string if the line is null or undefined.
        lineNumberText: function(line) {
            return line && line.lineNumber ? line.lineNumber : '';
        },
        // Render a line of text with indentation based on its level in the JSON structure.
        renderLine: function(line) {
            if (!line) {
                return '';
            }
            const indentation = '  '.repeat(line.level || 0);
            return `${indentation}${line.text}${line.comma ? ',' : ''}`;
        },
        // mirror the scroll position of the other pane when one pane is scrolled
        onPaneScroll: function(sourcePane) {
            // Prevent recursive scroll events from causing an infinite loop.
            if (this.isSyncingScroll) {
                return;
            }

            // Mirror the scroll position so both panes stay aligned.
            const sourceRef = sourcePane === 'left' ? 'leftPane' : 'rightPane';
            const targetRef = sourcePane === 'left' ? 'rightPane' : 'leftPane';
            const sourceElement = this.$refs[sourceRef];
            const targetElement = this.$refs[targetRef];

            if (!sourceElement || !targetElement) {
                return;
            }

            this.isSyncingScroll = true;
            // Set the target pane's scroll position to match the source pane's scroll position.
            targetElement.scrollTop = sourceElement.scrollTop;
            targetElement.scrollLeft = sourceElement.scrollLeft;
            // Use requestAnimationFrame to reset the syncing flag after the scroll event has been processed.
            requestAnimationFrame(() => {
                this.isSyncingScroll = false;
            });
        },
        // Reset the scroll position of both panes to the top-left corner.
        resetPaneScrollPosition: function() {
            const leftElement = this.$refs.leftPane;
            const rightElement = this.$refs.rightPane;

            if (leftElement) {
                leftElement.scrollTop = 0;
                leftElement.scrollLeft = 0;
            }

            if (rightElement) {
                rightElement.scrollTop = 0;
                rightElement.scrollLeft = 0;
            }
        },
        // Match the height of each diff row between left and right panes while allowing line wrap.
        syncRowHeights: function() {
            const leftPane = this.$refs.leftPane;
            const rightPane = this.$refs.rightPane;

            if (!leftPane || !rightPane) {
                return;
            }

            const leftRows = leftPane.querySelectorAll('tr');
            const rightRows = rightPane.querySelectorAll('tr');
            const rowCount = Math.max(leftRows.length, rightRows.length);

            // Reset inline heights before measuring to avoid stale values.
            for (let index = 0; index < rowCount; index++) {
                if (leftRows[index]) {
                    leftRows[index].style.height = '';
                }
                if (rightRows[index]) {
                    rightRows[index].style.height = '';
                }
            }

            // Use the taller row height for each row pair so both sides stay aligned.
            for (let index = 0; index < rowCount; index++) {
                const leftRow = leftRows[index];
                const rightRow = rightRows[index];
                const leftHeight = leftRow ? leftRow.offsetHeight : 0;
                const rightHeight = rightRow ? rightRow.offsetHeight : 0;
                const maxHeight = Math.max(leftHeight, rightHeight);

                if (leftRow) {
                    leftRow.style.height = `${maxHeight}px`;
                }
                if (rightRow) {
                    rightRow.style.height = `${maxHeight}px`;
                }
            }
        },

    },
}
</script>

<style scoped>
.compare-summary,
.compare-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
}

.compare-toggle {
    margin-bottom: 12px;
    color: #4b5563;
}

.compare-summary {
    align-items: center;
}

.compare-summary-text,
.legend-chip,
.compare-badge {
    font-weight: 600;
}

.compare-summary-text {
    color: #6b7280;
}

.compare-badge,
.legend-chip {
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 0.8rem;
}

.compare-badge-current { background: #e8f3ff; color: #245269; }
.compare-badge-previous { background: #f4ece8; color: #8a5a44; }
.legend-chip-equal { background: #f3f4f6; color: #4b5563; }
.legend-chip-modify { background: #fff7e6; color: #8a6d3b; }
.legend-chip-add { background: #edf7ea; color: #4c7a4c; }
.legend-chip-remove { background: #fceeee; color: #a94442; }

.json-diff-layout {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    width: 100%;
}

.json-diff-panel {
    overflow: hidden;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    background: #fff;
    min-width: 0;
    width: 100%;
}

.json-diff-panel-header {
    padding: 10px 12px;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
    color: #374151;
    font-weight: 700;
}

.json-diff-table { margin-bottom: 0; table-layout: fixed; }
.json-diff-table tbody { display: block; max-height: 65vh; overflow: auto; }
.json-diff-table tr { display: table; table-layout: fixed; width: 100%; }

.line-number-cell {
    width: 64px;
    background: #fafafa;
    color: #9ca3af;
    font-family: Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
    font-size: 0.8rem;
    text-align: right;
    user-select: none;
    vertical-align: top;
}

.json-diff-cell { padding: 0; vertical-align: top; }
.json-diff-cell-equal { background: #fff; }
.json-diff-cell-modify { background: #fffdf2; }
.json-diff-cell-add { background: #f5fbf2; }
.json-diff-cell-remove { background: #fff4f4; }

.json-diff-line {
    margin: 0;
    padding: 6px 10px;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
    font-size: 0.82rem;
    line-height: 1.45;
    background: transparent;
    border: 0;
}

@media (max-width: 992px) {
    .json-diff-layout { grid-template-columns: 1fr; }
}
</style>