import {Circle as CircleStyle, Fill, Stroke, Style, Icon} from 'ol/style';

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
            return new Stroke({color: SiteColours.not_to_be_reissued.stroke, width: stroke_width})
        case 'denied':
            return new Stroke({color: SiteColours.denied.stroke, width: stroke_width})
        case 'vacant':
            return new Stroke({color: SiteColours.vacant.stroke, width: stroke_width})
    }
}
export function getApiaryFeatureStyle(status){
    switch(status){
        case 'pending':
            return new Style({
                image: new CircleStyle({
                    radius: 5,
                    fill: new Fill({
                        color: '#0070FF'
                        //color: '#FFAA00'
                    }),
                    stroke: new Stroke({
                        color: '#000000',
                        width: 1
                    })
                })
            });
            break;
        case 'current':
            return new Style({
                image: new CircleStyle({
                    radius: 5,
                    fill: new Fill({
                        color: '#00FF00'
                    }),
                    stroke: new Stroke({
                        color: '#000000',
                        width: 1
                    })
                })
            });
            break;
        case 'suspended':
            return new Style({
                image: new CircleStyle({
                    radius: 5,
                    fill: new Fill({
                        color: '#FFFFFF'
                    }),
                    stroke: new Stroke({
                        color: '#000000',
                        width: 1
                    })
                })
            });
            break;
        case 'not_to_be_reissued':
            return new Style({
                image: new CircleStyle({
                    radius: 5,
                    fill: new Fill({
                        color: '#FF0000'
                    }),
                    stroke: new Stroke({
                        color: '#000000',
                        width: 1
                    })
                })
            });
            break;
        case 'denied':
            return new Style({
                image: new Icon({
                    color: '#000000',
                    //src: "data/x2.png"
                    src: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwgAADsIBFShKgAAAABl0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMC4xMzQDW3oAAACMSURBVChTlZDbDYAwDAM7AAOw/ypISEyAEMOUXHDS8viAk0xDYkPbUmv9pShgMg3lBj3NIAOrv95C1OoBngyMaoCHpN6M5wzoa31olsDN8rQAMDBtpoDazWD1I8A2FlNA3Z+pBRiYYs+7BHkRtp4PGhpAHPDtIjJwMfsvDWr1AE8G4GIO6GkGGfioWg6CRJYCwPQeRwAAAABJRU5ErkJggg=="
                })
            });
            break;
        case 'vacant':
            return new Style({
                image: new CircleStyle({
                    radius: 5,
                    fill: new Fill({
                        color: '#FFAA00'
                        //color: '#0070FF'
                    }),
                    stroke: new Stroke({
                        color: '#000000',
                        width: 1
                    })
                })
            });
            break;
        case 'dpaw_pool_of_sites':
            return new Style({
                image: new Icon({
                color: '#A900E6',
                    //src: "data/+2.png"
                    src: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuMTM0A1t6AAAAQklEQVQoU52LMQoAIBDD/P+n69KAmBvEQJaGriSToKahgpqGCmoaKqhpqKB2xie+DpOgpqGCmoYKahoqqGmocO1ZGzz92jSqmlDHAAAAAElFTkSuQmCC"
                }),
            });
            break;
        default:
            return new Style({
                image: new CircleStyle({
                    radius: 5,
                    fill: new Fill({
                        color: '#FF00FF'
                    }),
                    stroke: new Stroke({
                        color: '#00FF00',
                        width: 2
                    })
                })
            });
            break;
    }


}
