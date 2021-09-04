import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TopRowComponent } from './top-row.component';

describe('TopRowComponent', () => {
  let component: TopRowComponent;
  let fixture: ComponentFixture<TopRowComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TopRowComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TopRowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
