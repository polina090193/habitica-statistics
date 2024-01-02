export default function dateAdapter(date) {
  const parts = date.split('-');
  if (parts.length === 3) {
    const [year, month, day] = parts;
    return `${day}.${month}.${year}`;
  } else {
    return 'Invalid date format';
  }
}