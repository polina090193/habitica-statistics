export const getMonthsList = () => {
  const formatter = new Intl.DateTimeFormat('en-US', { month: 'long' });
  const monthNames = [];
  
  for (let month = 0; month < 12; month++) {
    const date = new Date(2000, month, 1);
    const monthName = formatter.format(date);
    monthNames.push(monthName);
  }

  return monthNames;
}
