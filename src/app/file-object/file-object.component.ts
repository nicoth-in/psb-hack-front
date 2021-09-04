import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-file-object',
  templateUrl: './file-object.component.html',
  styleUrls: ['./file-object.component.css']
})
export class FileObjectComponent implements OnInit {

  @Input() name = '';

  constructor() { }

  ngOnInit(): void {
  }

}
