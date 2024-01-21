import React, { useState } from 'react';
import TabularData from './TabularData';
import './MainPage.css';

export default function MainPage() {

    return (

      <div className='RenderedData'>
          <div className='Header'>
            Tire Change Shop Schedule
          </div>
          <div className='mainContent'>
            <TabularData />
          </div>
          <div className='Footer'>
            Hackathon Project
          </div>
      </div>
    );
}
