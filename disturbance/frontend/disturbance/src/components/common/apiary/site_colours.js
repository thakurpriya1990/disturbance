import {Circle as CircleStyle, Fill, Stroke, Style, Icon} from 'ol/style';

export const SiteColours = {
    'draft': {
        'fill': '#e0e0e0',
        'stroke': '#616161',
    },
    'pending': {
        'fill': '#0070FF',
        'stroke': '#00000',
    },
    'current': {
        'fill': '#00ff00', 
        'stroke': '#000000',
    },
    'approved': {
        'fill': '#00ff00', 
        'stroke': '#000000',
    },
    'suspended': {
        'fill': '#ffffff',
        'stroke': '#000000',
    },
    'not_to_be_reissued': {
        'fill': '#ff0000',
        'stroke': '#000000',
    },
    'denied': {
        'fill': '#000000',
        'stroke': '#000000',
        'icon_colour': '#000000',
    },
    'vacant': {
        'fill': '#ffaa00',
        'stroke': '#000000'
    },
    'dpaw_pool_of_sites': {
        'fill': '#a900e6',
        'stroke': '#000000',
        'icon_colour': '#a900e6',
    },
    'default': {
        'fill': '#ff00ff',
        'stroke': '#00ff00'
    }
}
export default SiteColours
export let existingSiteRadius = 5
export let drawingSiteRadius = 7
export function getApiaryFeatureStyle(status, selected=false, stroke_width_when_selected=2){
    console.log('in getApiaryFeatureStyle')
    let additional_width = selected ? stroke_width_when_selected : 0
    switch(status){
        case 'pending':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.pending.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.pending.stroke,
                        width: 1 + additional_width
                    })
                })
            });
            break;
        case 'current':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.current.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.current.stroke,
                        width: 1 + additional_width
                    })
                })
            });
            break;
        case 'approved':
            // Apiary site can be 'approved' status on a proposal
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.current.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.current.stroke,
                        width: 1 + additional_width
                    })
                })
            });
            break;
        case 'suspended':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.suspended.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.suspended.stroke,
                        width: 1 + additional_width
                    })
                })
            });
            break;
        case 'not_to_be_reissued':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.not_to_be_reissued.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.not_to_be_reissued.stroke,
                        width: 1 + additional_width
                    })
                })
            });
            break;
        case 'denied':
            return new Style({
                image: new Icon({
                    color: SiteColours.denied.icon_colour,
                    //src: "data/x2.png"
                    src: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwgAADsIBFShKgAAAABl0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMC4xMzQDW3oAAACMSURBVChTlZDbDYAwDAM7AAOw/ypISEyAEMOUXHDS8viAk0xDYkPbUmv9pShgMg3lBj3NIAOrv95C1OoBngyMaoCHpN6M5wzoa31olsDN8rQAMDBtpoDazWD1I8A2FlNA3Z+pBRiYYs+7BHkRtp4PGhpAHPDtIjJwMfsvDWr1AE8G4GIO6GkGGfioWg6CRJYCwPQeRwAAAABJRU5ErkJggg=="
                })
            });
            break;
        case 'vacant':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.vacant.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.vacant.stroke,
                        width: 1 + additional_width
                    })
                })
            });
            break;
        case 'dpaw_pool_of_sites':
            return new Style({
                image: new Icon({
                color: SiteColours.dpaw_pool_of_sites.icon_colour,
                    //src: "data/+2.png"
                    src: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuMTM0A1t6AAAAQklEQVQoU52LMQoAIBDD/P+n69KAmBvEQJaGriSToKahgpqGCmoaKqhpqKB2xie+DpOgpqGCmoYKahoqqGmocO1ZGzz92jSqmlDHAAAAAElFTkSuQmCC"
                }),
            });
            break;
        default:
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.default.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.default.stroke,
                        width: 2 + additional_width
                    })
                })
            });
            break;
    }
}
