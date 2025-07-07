import { GradeCalculator } from '../../src/utils/gradeCalculator';

describe('GradeCalculator', () => {
  describe('getGradePoint', () => {
    it('should return correct grade points', () => {
      expect(GradeCalculator.getGradePoint('A')).toBe(4.0);
      expect(GradeCalculator.getGradePoint('A-')).toBe(3.7);
      expect(GradeCalculator.getGradePoint('B+')).toBe(3.3);
      expect(GradeCalculator.getGradePoint('B')).toBe(3.0);
      expect(GradeCalculator.getGradePoint('E')).toBe(0.0);
    });

    it('should handle case insensitive input', () => {
      expect(GradeCalculator.getGradePoint('a')).toBe(4.0);
      expect(GradeCalculator.getGradePoint('b+')).toBe(3.3);
    });

    it('should return 0 for invalid grades', () => {
      expect(GradeCalculator.getGradePoint('X')).toBe(0);
      expect(GradeCalculator.getGradePoint('')).toBe(0);
    });
  });

  describe('getGradeFromNumber', () => {
    it('should return correct grade letters', () => {
      expect(GradeCalculator.getGradeFromNumber(95)).toBe('A');
      expect(GradeCalculator.getGradeFromNumber(82)).toBe('A-');
      expect(GradeCalculator.getGradeFromNumber(77)).toBe('B+');
      expect(GradeCalculator.getGradeFromNumber(30)).toBe('E');
    });

    it('should handle edge cases', () => {
      expect(GradeCalculator.getGradeFromNumber(85)).toBe('A');
      expect(GradeCalculator.getGradeFromNumber(84)).toBe('A-');
      expect(GradeCalculator.getGradeFromNumber(0)).toBe('E');
      expect(GradeCalculator.getGradeFromNumber(100)).toBe('A');
    });
  });

  describe('calculateIPS', () => {
    it('should calculate IPS correctly', () => {
      const nilaiData = [
        { sks: 3, nilai_huruf: 'A' },
        { sks: 3, nilai_huruf: 'B+' },
        { sks: 2, nilai_huruf: 'B' },
      ];

      const ips = GradeCalculator.calculateIPS(nilaiData);
      const expected = (3 * 4.0 + 3 * 3.3 + 2 * 3.0) / 8;
      
      expect(ips).toBe(Math.round(expected * 100) / 100);
    });

    it('should return 0 for empty data', () => {
      expect(GradeCalculator.calculateIPS([])).toBe(0);
    });
  });

  describe('isPassingGrade', () => {
    it('should identify passing grades correctly', () => {
      expect(GradeCalculator.isPassingGrade('A')).toBe(true);
      expect(GradeCalculator.isPassingGrade('B')).toBe(true);
      expect(GradeCalculator.isPassingGrade('C')).toBe(true);
      expect(GradeCalculator.isPassingGrade('D')).toBe(false);
      expect(GradeCalculator.isPassingGrade('E')).toBe(false);
    });
  });
});