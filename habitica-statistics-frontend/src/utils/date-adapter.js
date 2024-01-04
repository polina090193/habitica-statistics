export const convertToBEFormat = (date) => {
  const parts = date.split('-');
  if (parts.length === 3) {
    const [year, month, day] = parts;
    return `${day}.${month}.${year}`;
  } else {
    return 'Invalid date format';
  }
}

export const parseDateStringToDate = (dateStr) => {
  const [day, month, year] = dateStr.split('.').map(Number);
  return new Date(year, month - 1, day);
}

export const dateAdapter = {
  convertToBEFormat,
  parseDateStringToDate
}
