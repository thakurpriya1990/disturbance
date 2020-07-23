import { Fill, Stroke } from 'ol/style';

const SiteColours = {
    'draft': {
        'fill': '#e0e0e0',
        'stroke': '#616161',
    },
    'pending': {
        'fill': '#fff59d',
        'stroke': '#f2cb29',
    },
    'current': {
        'fill': '#bbdefb', 
        'stroke': '#1a76d2',
    },
    'suspended': {
        'fill': '#ffcc80',
        'stroke': '#f57c01',
    },
    'not_to_be_reissued': {
        'fill': '#d1c4e9',
        'stroke': '#512da8',
    },
    'denied': {
        'fill': '#ffcdd2',
        'stroke': '#d2302f',
    },
    'vacant': {
        'fill': '#7fcac3',
        'stroke': '#00796b'
    }
}
export default SiteColours
export let existingSiteRadius = 5
export let drawingSiteRadius = 7
export function getFillColour(status){
    switch(status){
        case 'draft':
            return new Fill({color: SiteColours.draft.fill})
        case 'pending':
            return new Fill({color: SiteColours.pending.fill})
        case 'current':
            return new Fill({color: SiteColours.current.fill})
        case 'suspended':
            return new Fill({color: SiteColours.suspended.fill})
        case 'not_to_be_reissued':
            return new Fill({color: SiteColours.not_to_be_reissued.fill})
        case 'denied':
            return new Fill({color: SiteColours.denied.fill})
        case 'vacant':
            return new Fill({color: SiteColours.vacant.fill})
    }
}
export function getStrokeColour(status, selected=false){
    let stroke_width = selected ? 4 : 2
    switch(status){
        case 'draft':
            return new Stroke({color: SiteColours.draft.stroke, width: stroke_width})
        case 'pending':
            return new Stroke({color: SiteColours.pending.stroke, width: stroke_width})
        case 'current':
            return new Stroke({color: SiteColours.current.stroke, width: stroke_width})
        case 'suspended':
            return new Stroke({color: SiteColours.suspended.stroke, width: stroke_width})
        case 'not_to_be_reissued':
            return new Stroke({color: SiteColours.no_to_be_reissued.stroke, width: stroke_width})
        case 'denied':
            return new Stroke({color: SiteColours.denied.stroke, width: stroke_width})
        case 'vacant':
            return new Stroke({color: SiteColours.vacant.stroke, width: stroke_width})
    }
}
