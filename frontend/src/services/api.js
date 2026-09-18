// Replace these mock functions with FastAPI calls later.
export const getFactoryState = async () => ({ status: 'ONLINE' })
export const getSchedule = async () => ({ schedule: [] })
export const generateSchedule = async () => ({ schedule: [] })
export const applyDisruption = async (payload) => ({ ...payload, status: 'APPLIED' })
export const reoptimizeSchedule = async () => ({ status: 'COMPLETED', schedule: [] })
export const getAIExplanation = async () => ({ explanation: 'Schedule changed based on resource availability, priority and deadlines.' })
