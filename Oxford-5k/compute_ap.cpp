#include <fstream>
#include <iostream>
#include <set>
#include <string>
#include <vector>
#include <bits/stdc++.h>

using namespace std;

vector<string>
load_list(const string& fname)
{
  vector<string> ret;
  ifstream fobj(fname.c_str());
  if (!fobj.good()) { cerr << "File " << fname << " not found!\n"; exit(-1); }
  string line;
  while (getline(fobj, line)) {
    ret.push_back(line);
  }
  return ret;
}

template<class T>
set<T> vector_to_set(const vector<T>& vec)
{ return set<T>(vec.begin(), vec.end()); }

float
compute_ap(const set<string>& pos, const set<string>& amb, const vector<string>& ranked_list)
{
  float old_recall = 0.0;
  float old_precision = 1.0;
  float ap = 0.0;
  
  size_t intersect_size = 0;
  size_t i = 0;
  size_t j = 0;
  for ( ; i<ranked_list.size(); ++i) {
    if (amb.count(ranked_list[i])) continue;
    if (pos.count(ranked_list[i])) intersect_size++;

    float recall = intersect_size / (float)pos.size();
    float precision = intersect_size / (j + 1.0);

    ap += (recall - old_recall)*((old_precision + precision)/2.0);
	//cout << ranked_list[i] << endl;
    old_recall = recall;
    old_precision = precision;
    j++;
  }
  return ap;
}

float evaluate(const string &gtq, const string & rank_list_file)
{
  string ground_truth_folder = "GroundTruth/";

  vector<string> ranked_list = load_list(rank_list_file);
  set<string> good_set = vector_to_set( load_list(ground_truth_folder + gtq + "_good.txt") );
  set<string> ok_set = vector_to_set( load_list(ground_truth_folder + gtq + "_ok.txt") );
  set<string> junk_set = vector_to_set( load_list(ground_truth_folder + gtq + "_junk.txt") );

  set<string> pos_set;
  pos_set.insert(good_set.begin(), good_set.end());
  pos_set.insert(ok_set.begin(), ok_set.end());

  
  float ap = compute_ap(pos_set, junk_set, ranked_list);
  
  return ap;
}

int main(int argc, char **argv){
	ifstream in;
	if(argc < 2) {
		cout << "Please give feature type!" << endl;
    return 0;
	}
  cout << argv[1] << endl;
	string feature_folder(argv[1]);
	in.open("query_list.txt", ios::in);
	string query;
	float precision = 0;
	int count = 0;
	while(in >> query) {
		float p = evaluate(query, feature_folder + "/" + query + "_rank_list.txt");
		precision += p;
		cout << query << " " << p << endl;
		count += 1;
	}
	cout << endl;
	cout << precision / count << endl;
  return 0;
}

