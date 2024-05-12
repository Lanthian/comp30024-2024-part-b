/**
 * Takes in a selection of binary "x/y" ratios and sums ratio parts. 
 * @param {number|Array<Array<number>>} input The value or range of cells with ratios to combine
 * @return "x1+x2+...+xn / y1+y2+...+yn"
 * @customfunction
 * @author Liam Anthian, 2024.05.12
 */
function SUM_RATIO(input) {
  // Separating delimiter between ratio values
  const DELIM = '/'

  if (Array.isArray(input)) {
    var x = 0;
    var y = 0;

    // Iterate over each individual cell
    for (var i = 0; i<input.length; i++) {
      for (var j = 0; j<input[i].length; j++) {

        var ratios = String(input[i][j]).split(DELIM)
        x += parseInt(ratios[0])
        y += parseInt(ratios[1])
      }
    }
    return String(x) + DELIM + String(y)
  }
  
  // If only one cell selected, return its value
  else {
    return input;
  }
}


/**
 * Subtracts a ratio from another ratio
 * @param i1 The "x/y" ratio that is subtracted from
 * @param i2 The "x/y" ratio that is subtracted
 * @return "x1-x2/y1-y2"
 * @customfunction
 * @author Liam Anthian, 2024.05.12
 */
function MINUS_RATIO(i1, i2) {
  r1 = String(i1).split('/')
  r2 = String(i2).split('/')
  
  var numerator = parseInt(r1[0]) - parseInt(r2[0]);
  var denominator = parseInt(r1[1]) - parseInt(r2[1]);

  return String(numerator) + "/" + String(denominator)
}
