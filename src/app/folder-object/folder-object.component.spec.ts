import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FolderObjectComponent } from './folder-object.component';

describe('FolderObjectComponent', () => {
  let component: FolderObjectComponent;
  let fixture: ComponentFixture<FolderObjectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FolderObjectComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FolderObjectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
