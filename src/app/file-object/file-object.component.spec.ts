import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FileObjectComponent } from './file-object.component';

describe('FileObjectComponent', () => {
  let component: FileObjectComponent;
  let fixture: ComponentFixture<FileObjectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FileObjectComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FileObjectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
