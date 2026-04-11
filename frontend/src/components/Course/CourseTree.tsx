import React from 'react';

export const CourseTree: React.FC = () => {
  return (
    <div>
      <h4>Course Tree</h4>
      <ul>
        <li>Course A
          <ul>
            <li>Chapter 1</li>
            <li>Chapter 2</li>
          </ul>
        </li>
        <li>Course B</li>
      </ul>
    </div>
  );
};
