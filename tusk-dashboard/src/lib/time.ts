/** MSFLib stores timestamps as naive UTC. */
export const utc = (iso: string) => (/[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`);
